import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppError
from app.models.user import User

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise AppError(status_code=401, detail="Token expirado.")
    except jwt.PyJWTError:
        raise AppError(status_code=401, detail="Token inválido.")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AppError(status_code=401, detail="Usuário não encontrado.")

    if not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise AppError(status_code=403, detail="Acesso restrito a administradores.")
    return current_user
