from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    cpf: Optional[str]
    cnpj: Optional[str]
    is_admin: bool
    is_team_member: bool

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "cliente@garagehub.com",
                "password": "senha123",
                "cpf": "123.456.789-09",
            }
        }
    }


class UserUpdate(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None


class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_team_member: Optional[bool] = None
