from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import AppError, app_error_handler

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Endpoints para verificação de saúde e disponibilidade da API.",
    },
    {
        "name": "auth",
        "description": "Endpoints de autenticação — login e geração de tokens JWT.",
    },
    {
        "name": "users",
        "description": "CRUD de usuários — criação, consulta, atualização e desativação.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=(
            "API do **GarageHub** — plataforma de gestão de oficinas mecânicas.\n\n"
            "## Autenticação\n"
            "Todos os endpoints protegidos exigem um token Bearer no header `Authorization`.\n\n"
            "## Versionamento\n"
            "A versão atual da API é `v1`. O prefixo de todas as rotas é `/api/v1`."
        ),
        contact={"name": "GarageHub Team", "email": "dev@garagehub.com"},
        license_info={"name": "MIT"},
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    app.openapi_schema = schema
    return schema


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.APP_DEBUG,
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    app.openapi = lambda: custom_openapi(app)  # type: ignore[method-assign]
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
