from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import CustomerType


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    cpf: Optional[str]
    cnpj: Optional[str]
    customer_type: CustomerType
    is_admin: bool
    is_team_member: bool

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    customer_type: CustomerType = CustomerType.pessoa_fisica

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "cliente@garagehub.com",
                "password": "senha123",
                "cpf": "123.456.789-09",
                "customer_type": "pessoa_fisica",
            }
        }
    }


class UserUpdate(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    is_active: Optional[bool] = None
