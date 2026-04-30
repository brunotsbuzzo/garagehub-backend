import uuid
from typing import Callable, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.enums import UserRole
from app.core.rbac import Permission
from app.models.blacklisted_token import BlacklistedToken
from app.models.user import User

http_bearer = HTTPBearer()


async def get_jwt_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    """Decodifica e valida o JWT. Não consulta o banco."""
    try:
        return jwt.decode(
            credentials.credentials,
            settings.APP_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise AppError(status_code=401, detail="Token expirado.")
    except jwt.PyJWTError:
        raise AppError(status_code=401, detail="Token inválido.")


async def get_current_user(
    payload: dict = Depends(get_jwt_payload),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida blacklist, carrega o usuário e verifica se está ativo."""
    user_id: str = payload["sub"]
    jti: Optional[str] = payload.get("jti")

    if jti:
        result = await db.execute(
            select(BlacklistedToken).where(BlacklistedToken.jti == jti)
        )
        if result.scalar_one_or_none():
            raise AppError(status_code=401, detail="Token revogado.")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AppError(status_code=401, detail="Usuário não encontrado.")
    if not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    return user


def require_roles(*required_roles: UserRole) -> Callable:
    """
    Dependência que exige pelo menos um dos papéis na claim 'roles' do JWT.
    A verificação é feita diretamente no payload — sem consulta extra ao banco.
    """
    async def dependency(
        payload: dict = Depends(get_jwt_payload),
        user: User = Depends(get_current_user),
    ) -> User:
        token_roles: list[str] = payload.get("roles", [])
        if not any(r.value in token_roles for r in required_roles):
            raise AppError(
                status_code=403,
                detail=f"Papel insuficiente. Exigido: {[r.value for r in required_roles]}.",
            )
        return user

    return dependency


def require_permissions(*required_permissions: Permission) -> Callable:
    """
    Dependência que exige pelo menos uma das permissões na claim 'permissions' do JWT.
    A verificação é feita diretamente no payload — sem consulta extra ao banco.
    """
    async def dependency(
        payload: dict = Depends(get_jwt_payload),
        user: User = Depends(get_current_user),
    ) -> User:
        token_perms: list[str] = payload.get("permissions", [])
        if not any(p.value in token_perms for p in required_permissions):
            raise AppError(
                status_code=403,
                detail=f"Permissão insuficiente. Exigida: {[p.value for p in required_permissions]}.",
            )
        return user

    return dependency


async def get_current_admin(
    user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
) -> User:
    return user
