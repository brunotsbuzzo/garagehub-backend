from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Autenticar usuário")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    access_token = await auth_service.login(body.email, body.password, db)
    return TokenResponse(access_token=access_token)
