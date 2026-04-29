from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.models.user import User


async def login(email: str, password: str, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AppError(status_code=401, detail="Credenciais inválidas.")

    if not user.is_active:
        raise AppError(status_code=403, detail="Usuário inativo.")

    return create_access_token(subject=str(user.id))
