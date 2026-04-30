import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User


async def login(email: str, password: str, db: AsyncSession) -> tuple[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AppError(status_code=401, detail="Credenciais inválidas.")

    if not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    access_token = create_access_token(subject=str(user.id))
    refresh_token = await _create_refresh_token(user.id, db)
    return access_token, refresh_token


async def refresh(refresh_token_value: str, db: AsyncSession) -> tuple[str, str]:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token_value)
    )
    token = result.scalar_one_or_none()

    if not token or token.revoked or token.expires_at < datetime.now(timezone.utc):
        raise AppError(status_code=401, detail="Refresh token inválido ou expirado.")

    # rotaciona: revoga o token atual e emite um novo par
    token.revoked = True
    await db.flush()

    access_token = create_access_token(subject=str(token.user_id))
    new_refresh_token = await _create_refresh_token(token.user_id, db)
    return access_token, new_refresh_token


async def logout(refresh_token_value: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token_value)
    )
    token = result.scalar_one_or_none()

    if not token or token.revoked:
        raise AppError(status_code=401, detail="Refresh token inválido.")

    token.revoked = True
    await db.commit()


async def _create_refresh_token(user_id: uuid.UUID, db: AsyncSession) -> str:
    token_value = RefreshToken.generate()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=token_value, user_id=user_id, expires_at=expires_at))
    await db.commit()
    return token_value
