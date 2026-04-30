from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Valida credenciais e retorna um access token (JWT) e um refresh token.",
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = await auth_service.login(body.email, body.password, db)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
    description=(
        "Emite um novo par de tokens a partir de um refresh token válido. "
        "O refresh token utilizado é revogado (rotação automática)."
    ),
)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = await auth_service.refresh(body.refresh_token, db)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=204,
    summary="Encerrar sessão",
    description="Revoga o refresh token, encerrando a sessão do usuário.",
)
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)) -> None:
    await auth_service.logout(body.refresh_token, db)
