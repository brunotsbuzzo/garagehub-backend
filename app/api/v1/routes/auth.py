import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, http_bearer
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenData, TokenResponse
from app.schemas.session import SessionResponse
from app.services import auth as auth_service

router = APIRouter()


def _build_token_response(access_token: str, refresh_token: str, message: str) -> TokenResponse:
    return TokenResponse(
        data=TokenData(access_token=access_token, refresh_token=refresh_token),
        message=message,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description=(
        "Valida credenciais, revoga sessões ativas do mesmo dispositivo, "
        "respeita o limite de sessões simultâneas e emite novo par de tokens."
    ),
)
async def login(
    body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    access_token, refresh_token = await auth_service.login(
        body.email, body.password, db, ip_address=ip, user_agent=user_agent
    )
    return _build_token_response(access_token, refresh_token, "Login realizado com sucesso.")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
    description="Valida o refresh token, revoga-o e emite novo par (rotação automática).",
)
async def refresh(
    body: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    access_token, refresh_token = await auth_service.refresh(
        body.refresh_token, db, ip_address=ip, user_agent=user_agent
    )
    return _build_token_response(access_token, refresh_token, "Tokens atualizados com sucesso.")


@router.post(
    "/logout",
    status_code=204,
    summary="Encerrar sessão",
    description="Revoga o refresh token e adiciona o access token à blacklist.",
)
async def logout(
    body: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    payload = decode_token(credentials.credentials)
    jti = payload.get("jti")
    await auth_service.logout(body.refresh_token, jti, current_user.id, db)


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    summary="Listar sessões ativas",
    description="Retorna todas as sessões ativas do usuário autenticado.",
)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    return await auth_service.list_sessions(current_user.id, db)


@router.delete(
    "/sessions",
    status_code=204,
    summary="Encerrar todas as sessões",
    description="Revoga todos os refresh tokens do usuário e blacklista o access token atual.",
)
async def logout_all(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    payload = decode_token(credentials.credentials)
    jti = payload.get("jti")
    await auth_service.logout_all(current_user.id, jti, db)


@router.delete(
    "/sessions/{session_id}",
    status_code=204,
    summary="Revogar sessão específica",
    description="Revoga uma sessão ativa pelo ID. O usuário só pode revogar suas próprias sessões.",
)
async def revoke_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await auth_service.revoke_session(session_id, current_user.id, db)
