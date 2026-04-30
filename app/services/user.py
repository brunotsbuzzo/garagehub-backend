import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserCreate, UserUpdate


async def create_user(data: UserCreate, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise AppError(status_code=409, detail="E-mail já cadastrado.")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        cpf=data.cpf,
        cnpj=data.cnpj,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_user(user_id: uuid.UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppError(status_code=404, detail="Usuário não encontrado.")
    return user


async def update_user(user: User, data: UserUpdate | UserAdminUpdate, db: AsyncSession) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(user: User, db: AsyncSession) -> None:
    user.is_active = False
    await db.commit()
