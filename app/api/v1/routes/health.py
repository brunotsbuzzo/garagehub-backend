from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado atual da API.", examples=["ok"])

    model_config = {"json_schema_extra": {"example": {"status": "ok"}}}


@router.get(
    "",
    response_model=HealthResponse,
    summary="Verificar saúde da API",
    description="Retorna `ok` se a API estiver disponível e aceitando requisições.",
    responses={200: {"description": "API operacional."}},
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
