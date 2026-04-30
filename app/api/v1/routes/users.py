import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserCreate, UserResponse, UserUpdate
from app.services import user as user_service

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Criar usuário",
    description="Cria um novo usuário. Não requer autenticação.",
)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    return await user_service.create_user(body, db)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuários",
    description="Retorna todos os usuários. Requer perfil de administrador.",
)
async def list_users(
    skip: Annotated[int, Query(ge=0, description="Registros a pular")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo de registros")] = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[User]:
    return await user_service.list_users(db, skip=skip, limit=limit)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter usuário autenticado",
    description="Retorna os dados do usuário autenticado.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Retorna os dados de um usuário pelo ID. Requer perfil de administrador.",
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    return await user_service.get_user(user_id, db)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Atualizar usuário autenticado",
    description="Atualiza os dados do usuário autenticado (CPF, CNPJ, tipo de cliente).",
)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return await user_service.update_user(current_user, body, db)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário por ID",
    description="Atualiza os dados de um usuário pelo ID. Requer perfil de administrador.",
)
async def update_user_by_id(
    user_id: uuid.UUID,
    body: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    user = await user_service.get_user(user_id, db)
    return await user_service.update_user(user, body, db)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Desativar usuário",
    description="Desativa um usuário (soft delete). Requer perfil de administrador.",
)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> None:
    user = await user_service.get_user(user_id, db)
    await user_service.deactivate_user(user, db)
