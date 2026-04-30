# Desenvolvimento

Este guia cobre o processo completo para implementar um novo recurso na API, desde o model até os testes.

---

## Estrutura de um recurso

Cada recurso segue a mesma estrutura de camadas:

```
app/
├── models/       ← definição da tabela (SQLAlchemy)
├── schemas/      ← validação de entrada/saída (Pydantic)
├── services/     ← regras de negócio (sem HTTP)
└── api/v1/
    └── routes/   ← endpoints HTTP (FastAPI)
```

---

## Passo a passo: criando um novo recurso

O exemplo abaixo cria o recurso `Vehicle` (veículo) do zero.

---

### 1. Model (`app/models/vehicle.py`)

Herde `UUIDMixin`, `TimestampMixin` e `Base`:

```python
from typing import Optional
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Vehicle(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "vehicles"

    plate: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
```

**Mixins disponíveis:**

| Mixin | O que fornece |
|---|---|
| `UUIDMixin` | `id: UUID` como chave primária |
| `TimestampMixin` | `created_at` e `updated_at` automáticos |

Registre o model no Alembic (`alembic/env.py`):

```python
from app.models.vehicle import Vehicle  # noqa: F401
```

---

### 2. Migration

```bash
alembic revision --autogenerate -m "create vehicles table"
alembic upgrade head
```

Revise o arquivo gerado em `alembic/versions/` antes de aplicar — o autogenerate não detecta tudo (ex: enums, índices compostos).

---

### 3. Schemas (`app/schemas/vehicle.py`)

Defina um schema para cada operação:

```python
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VehicleResponse(BaseModel):
    id: UUID
    plate: str
    brand: str
    model: str
    year: int
    owner_id: UUID
    notes: Optional[str]

    model_config = {"from_attributes": True}


class VehicleCreate(BaseModel):
    plate: str
    brand: str
    model: str
    year: int
    notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "plate": "ABC-1234",
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2022,
            }
        }
    }


class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    notes: Optional[str] = None
```

**Convenções:**

| Schema | Propósito |
|---|---|
| `XxxResponse` | Saída dos endpoints (o que o cliente recebe) |
| `XxxCreate` | Corpo do `POST` |
| `XxxUpdate` | Corpo do `PATCH` — todos os campos opcionais |
| `XxxAdminUpdate` | Extensão de `XxxUpdate` com campos restritos a admins |

---

### 4. Service (`app/services/vehicle.py`)

A camada de serviço contém toda a lógica de negócio. Não deve conhecer HTTP, `Request` ou `Response`.

```python
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def create_vehicle(
    data: VehicleCreate, owner_id: uuid.UUID, db: AsyncSession
) -> Vehicle:
    result = await db.execute(select(Vehicle).where(Vehicle.plate == data.plate))
    if result.scalar_one_or_none():
        raise AppError(status_code=409, detail="Placa já cadastrada.")

    vehicle = Vehicle(**data.model_dump(), owner_id=owner_id)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


async def list_vehicles(
    owner_id: uuid.UUID, db: AsyncSession, skip: int = 0, limit: int = 50
) -> list[Vehicle]:
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_vehicle(vehicle_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> Vehicle:
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.owner_id == owner_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise AppError(status_code=404, detail="Veículo não encontrado.")
    return vehicle


async def update_vehicle(
    vehicle: Vehicle, data: VehicleUpdate, db: AsyncSession
) -> Vehicle:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


async def delete_vehicle(vehicle: Vehicle, db: AsyncSession) -> None:
    await db.delete(vehicle)
    await db.commit()
```

**Padrões obrigatórios:**

- Use `AppError(status_code=..., detail="...")` para erros de negócio — nunca `HTTPException`
- Use `model_dump(exclude_unset=True)` em updates parciais (PATCH)
- Sempre faça `await db.refresh(obj)` após commit para garantir que os campos gerados pelo banco (como `created_at`) estejam populados

---

### 5. Permissões RBAC (`app/core/rbac.py`)

Adicione as novas permissões antes de criar as rotas:

```python
class Permission(str, Enum):
    # ... existentes ...
    VEHICLE_READ  = "vehicle:read"
    VEHICLE_WRITE = "vehicle:write"
    VEHICLE_DELETE = "vehicle:delete"
```

Atribua aos papéis no mapeamento:

```python
ROLE_PERMISSIONS = {
    Role.CUSTOMER: frozenset({
        ...
        Permission.VEHICLE_READ,
        Permission.VEHICLE_WRITE,   # dono pode editar seus próprios veículos
        Permission.VEHICLE_DELETE,
    }),
    Role.TEAM_MEMBER: frozenset({
        ...
        Permission.VEHICLE_READ,
        Permission.VEHICLE_WRITE,
    }),
    Role.ADMIN: frozenset({
        ...
        Permission.VEHICLE_READ,
        Permission.VEHICLE_WRITE,
        Permission.VEHICLE_DELETE,
    }),
}
```

Consulte [Controle de Acesso (RBAC)](rbac.md) para o guia completo.

---

### 6. Rotas (`app/api/v1/routes/vehicles.py`)

```python
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permissions
from app.core.rbac import Permission
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services import vehicle as vehicle_service

router = APIRouter()


@router.post("", response_model=VehicleResponse, status_code=201, summary="Cadastrar veículo")
async def create_vehicle(
    body: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.VEHICLE_WRITE)),
) -> Vehicle:
    return await vehicle_service.create_vehicle(body, current_user.id, db)


@router.get("", response_model=list[VehicleResponse], summary="Listar veículos")
async def list_vehicles(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.VEHICLE_READ)),
) -> list:
    return await vehicle_service.list_vehicles(current_user.id, db, skip=skip, limit=limit)


@router.get("/{vehicle_id}", response_model=VehicleResponse, summary="Obter veículo")
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.VEHICLE_READ)),
) -> Vehicle:
    return await vehicle_service.get_vehicle(vehicle_id, current_user.id, db)


@router.patch("/{vehicle_id}", response_model=VehicleResponse, summary="Atualizar veículo")
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.VEHICLE_WRITE)),
) -> Vehicle:
    vehicle = await vehicle_service.get_vehicle(vehicle_id, current_user.id, db)
    return await vehicle_service.update_vehicle(vehicle, body, db)


@router.delete("/{vehicle_id}", status_code=204, summary="Remover veículo")
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.VEHICLE_DELETE)),
) -> None:
    vehicle = await vehicle_service.get_vehicle(vehicle_id, current_user.id, db)
    await vehicle_service.delete_vehicle(vehicle, db)
```

**Dependências disponíveis:**

| Dependência | Uso |
|---|---|
| `get_current_user` | Qualquer usuário autenticado |
| `require_roles(Role.ADMIN)` | Somente admins |
| `require_permissions(Permission.X)` | Quem tiver a permissão X |
| `get_current_admin` | Atalho para `require_roles(Role.ADMIN)` |

---

### 7. Registro do router (`app/api/v1/router.py`)

```python
from app.api.v1.routes import auth, health, users, vehicles  # ← importar

router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
```

---

### 8. Tag OpenAPI (`app/main.py`)

```python
OPENAPI_TAGS = [
    ...
    {
        "name": "vehicles",
        "description": "Gerenciamento de veículos dos clientes.",
    },
]
```

---

### 9. Testes (`tests/test_vehicles.py`)

```python
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    # cria usuário e faz login para obter token
    await client.post("/api/v1/users", json={
        "email": "test@garagehub.com",
        "password": "senha123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@garagehub.com",
        "password": "senha123",
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_vehicle(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post(
        "/api/v1/vehicles",
        json={"plate": "ABC-1234", "brand": "Toyota", "model": "Corolla", "year": 2022},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plate"] == "ABC-1234"


async def test_create_vehicle_duplicate_plate(client: AsyncClient, auth_headers: dict) -> None:
    payload = {"plate": "XYZ-9999", "brand": "Honda", "model": "Civic", "year": 2021}
    await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)
    response = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)
    assert response.status_code == 409


async def test_list_vehicles_unauthenticated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/vehicles")
    assert response.status_code == 403
```

---

## Referência rápida

### Erros de negócio

```python
from app.core.exceptions import AppError

raise AppError(status_code=404, detail="Recurso não encontrado.")
raise AppError(status_code=409, detail="Conflito de dados.")
raise AppError(status_code=422, detail="Dado inválido.")
```

Todos os `AppError` retornam o formato padrão:

```json
{ "detail": "Mensagem do erro." }
```

### Banco de dados assíncrono

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# busca por PK
result = await db.execute(select(Model).where(Model.id == some_id))
obj = result.scalar_one_or_none()

# lista com filtros
result = await db.execute(
    select(Model)
    .where(Model.active == True)
    .order_by(Model.created_at.desc())
    .offset(skip)
    .limit(limit)
)
items = list(result.scalars().all())

# inserção
db.add(obj)
await db.commit()
await db.refresh(obj)

# update parcial (PATCH)
for field, value in data.model_dump(exclude_unset=True).items():
    setattr(obj, field, value)
await db.commit()
await db.refresh(obj)

# deleção física
await db.delete(obj)
await db.commit()
```

### Update parcial vs. completo

| Verbo HTTP | Schema | `model_dump` |
|---|---|---|
| `PUT` | todos os campos obrigatórios | `model_dump()` |
| `PATCH` | todos opcionais | `model_dump(exclude_unset=True)` |

### Paginação padrão

```python
from typing import Annotated
from fastapi import Query

skip:  Annotated[int, Query(ge=0)]        = 0
limit: Annotated[int, Query(ge=1, le=100)] = 50
```

---

## Checklist completo

- [ ] Model criado em `app/models/`
- [ ] Model importado em `alembic/env.py`
- [ ] Migration gerada e revisada (`alembic revision --autogenerate`)
- [ ] Migration aplicada (`alembic upgrade head`)
- [ ] Schemas `Response`, `Create` e `Update` criados em `app/schemas/`
- [ ] Service criado em `app/services/` usando `AppError` para erros
- [ ] Permissões adicionadas em `app/core/rbac.py` e atribuídas aos papéis
- [ ] Rotas criadas em `app/api/v1/routes/` com dependências RBAC corretas
- [ ] Router registrado em `app/api/v1/router.py`
- [ ] Tag OpenAPI adicionada em `app/main.py`
- [ ] Testes escritos em `tests/`
- [ ] Lint passando: `ruff check . --fix && ruff format .`
- [ ] Testes passando: `python3 -m pytest tests/ -v`

---

## Ferramentas

### Testes

```bash
python3 -m pytest tests/ -v            # todos os testes
python3 -m pytest tests/test_x.py -v  # arquivo específico
python3 -m pytest tests/ -v --cov=app  # com cobertura
```

### Lint e formato

```bash
ruff check . --fix   # corrige automaticamente
ruff format .        # formata o código
```

### Migrations

```bash
alembic revision --autogenerate -m "descricao"  # gera migration
alembic upgrade head                             # aplica todas
alembic downgrade -1                             # desfaz a última
alembic history                                  # histórico
alembic current                                  # versão aplicada
```

### Servidor de desenvolvimento

```bash
fastapi dev app/main.py   # hot reload + APP_DEBUG=true automático
```

Com `APP_DEBUG=true` no `.env`:

- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`
