import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.rbac import get_user_permissions, get_user_roles
from app.core.security import create_access_token, hash_token, verify_password
from app.models.blacklisted_token import BlacklistedToken
from app.models.refresh_token import RefreshToken
from app.models.user import User


async def login(
    email: str,
    password: str,
    db: AsyncSession,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> tuple[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AppError(status_code=401, detail="Credenciais inválidas.")

    if not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    await _revoke_device_sessions(user.id, ip_address, user_agent, db)
    await _enforce_session_limit(user.id, db)

    access_token = _build_access_token(user)
    refresh_token = await _create_refresh_token(
        user.id, db, ip_address=ip_address, user_agent=user_agent
    )
    return access_token, refresh_token


async def refresh(
    refresh_token_value: str,
    db: AsyncSession,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> tuple[str, str]:
    token_hash = hash_token(refresh_token_value)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token_hash))
    token = result.scalar_one_or_none()

    if not token or not token.is_valid:
        raise AppError(status_code=401, detail="Refresh token inválido ou expirado.")

    # carrega o usuário para refletir roles/permissões atuais
    user_result = await db.execute(select(User).where(User.id == token.user_id))
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    token.revoked_at = datetime.now(timezone.utc)
    await db.flush()

    access_token = _build_access_token(user)
    new_refresh_token = await _create_refresh_token(
        user.id, db, ip_address=ip_address, user_agent=user_agent
    )
    return access_token, new_refresh_token


async def logout(
    refresh_token_value: str,
    jti: Optional[str],
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    token_hash = hash_token(refresh_token_value)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token_hash))
    token = result.scalar_one_or_none()

    if not token or token.revoked_at is not None:
        raise AppError(status_code=401, detail="Refresh token inválido.")

    token.revoked_at = datetime.now(timezone.utc)

    if jti:
        await _blacklist_jti(jti, user_id, db)

    await db.commit()


async def logout_all(user_id: uuid.UUID, jti: Optional[str], db: AsyncSession) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    for token in result.scalars().all():
        token.revoked_at = datetime.now(timezone.utc)

    if jti:
        await _blacklist_jti(jti, user_id, db)

    await db.commit()


async def list_sessions(user_id: uuid.UUID, db: AsyncSession) -> list[RefreshToken]:
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        .order_by(RefreshToken.created_at.desc())
    )
    return list(result.scalars().all())


async def revoke_session(
    session_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise AppError(status_code=404, detail="Sessão não encontrada.")
    if token.revoked_at is not None:
        raise AppError(status_code=409, detail="Sessão já encerrada.")

    token.revoked_at = datetime.now(timezone.utc)
    await db.commit()


# ── helpers ──────────────────────────────────────────────────────────────────

def _build_access_token(user: User) -> str:
    roles = get_user_roles(user)
    permissions = get_user_permissions(roles)
    return create_access_token(
        subject=str(user.id),
        roles=[r.value for r in roles],
        permissions=[p.value for p in permissions],
    )


async def _revoke_device_sessions(
    user_id: uuid.UUID,
    ip_address: Optional[str],
    user_agent: Optional[str],
    db: AsyncSession,
) -> None:
    if not ip_address or not user_agent:
        return

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.ip_address == ip_address,
            RefreshToken.user_agent == user_agent,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    for token in result.scalars().all():
        token.revoked_at = datetime.now(timezone.utc)

    await db.flush()


async def _enforce_session_limit(user_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        .order_by(RefreshToken.created_at.asc())
    )
    active = result.scalars().all()

    excess = len(active) - (settings.MAX_ACTIVE_SESSIONS - 1)
    if excess > 0:
        for token in active[:excess]:
            token.revoked_at = datetime.now(timezone.utc)
        await db.flush()


async def _blacklist_jti(jti: str, user_id: uuid.UUID, db: AsyncSession) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    db.add(BlacklistedToken(jti=jti, user_id=user_id, expires_at=expires_at))


async def _create_refresh_token(
    user_id: uuid.UUID,
    db: AsyncSession,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> str:
    token_value = RefreshToken.generate()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(
        RefreshToken(
            token=hash_token(token_value),
            user_id=user_id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    await db.commit()
    return token_value
