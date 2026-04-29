# Banco de Dados

## Visão geral

O projeto usa **PostgreSQL 16** como banco de dados, acessado de forma assíncrona via **SQLAlchemy 2.0** com o driver **asyncpg**.

## Conexão

A conexão é gerenciada em `app/core/database.py`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,  # loga as queries SQL quando em modo debug
    pool_pre_ping=True,        # reconecta automaticamente se a conexão cair
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)
```

A sessão é injetada nos endpoints via dependency injection do FastAPI:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
```

## Models

Todos os models ficam em `app/models/` e herdam de `Base` (declarado em `app/models/base.py`).

### Mixins disponíveis

**`UUIDMixin`** — chave primária UUID v4 gerada automaticamente:

```python
class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
```

**`TimestampMixin`** — timestamps gerenciados pelo banco:

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Models existentes

#### `User` (`app/models/user.py`)

Representa um usuário autenticável da plataforma.

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `UUID` | Chave primária (gerada automaticamente) |
| `email` | `VARCHAR(255)` | Email único, indexado |
| `hashed_password` | `VARCHAR(255)` | Senha em hash bcrypt |
| `is_active` | `BOOLEAN` | Indica se o usuário pode se autenticar |
| `created_at` | `TIMESTAMPTZ` | Data de criação |
| `updated_at` | `TIMESTAMPTZ` | Data da última atualização |

### Exemplo de model completo

```python
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin

class Garage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "garages"

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str | None] = mapped_column(nullable=True)
```

## Migrations (Alembic)

As migrations ficam em `alembic/versions/` e são versionadas no git.

### Comandos principais

```bash
# aplicar todas as migrations pendentes
alembic upgrade head

# gerar nova migration automaticamente a partir dos models
alembic revision --autogenerate -m "descricao da mudanca"

# desfazer a última migration
alembic downgrade -1

# ver o estado atual
alembic current

# ver histórico de migrations
alembic history
```

### Como o autogenerate funciona

O `alembic/env.py` importa `Base.metadata` e detecta automaticamente qualquer model que herde de `Base`. Para que um novo model seja detectado, ele **deve ser importado** em `alembic/env.py`:

```python
from app.models.base import Base
from app.models import nome_do_model  # noqa: F401
```

!!! warning "Revise sempre o autogenerate"
    O Alembic detecta adições e remoções de tabelas/colunas, mas alguns casos (como renomeação) precisam de ajuste manual no arquivo de migration gerado. Sempre revise o arquivo antes de aplicar.
