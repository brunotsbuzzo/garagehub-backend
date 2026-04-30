from pydantic import BaseModel, EmailStr

from app.core.config import settings


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {"email": "mecanico@garagehub.com", "password": "senha123"}
        }
    }


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


class TokenResponse(BaseModel):
    data: TokenData
    quantity: int = 1
    message: str
    status_code: int = 200
