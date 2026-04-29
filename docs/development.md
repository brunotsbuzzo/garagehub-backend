# Desenvolvimento

## Testes

Os testes usam **pytest** com suporte a async via `pytest-asyncio` e cliente HTTP via `httpx`.

```bash
# rodar todos os testes
python3 -m pytest tests/ -v

# rodar com cobertura
python3 -m pytest tests/ -v --cov=app
```

## Linter e formatter

O projeto usa **Ruff** para lint e formatação (substitui flake8, isort e black).

```bash
# verificar
ruff check .

# corrigir automaticamente
ruff check . --fix

# formatar
ruff format .
```

As regras ativas estão configuradas em `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

| Conjunto | Descrição |
|---|---|
| `E` | Erros de estilo PEP 8 |
| `F` | Erros lógicos (pyflakes) |
| `I` | Ordenação de imports (isort) |
| `UP` | Modernização de sintaxe Python (pyupgrade) |

## Adicionando novos models

1. Crie o arquivo em `app/models/nome_do_model.py`
2. Herde de `Base` e use os mixins disponíveis:

```python
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin

class Garage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "garages"

    name: Mapped[str] = mapped_column(nullable=False)
```

3. Importe o model em `alembic/env.py` para que o autogenerate o detecte:

```python
from app.models import nome_do_model  # noqa: F401
```

4. Gere a migration:

```bash
alembic revision --autogenerate -m "add garages table"
alembic upgrade head
```

## Adicionando novos endpoints

1. Crie o arquivo em `app/api/v1/routes/nome_do_recurso.py`
2. Defina o `APIRouter` e os endpoints
3. Registre o router em `app/api/v1/router.py`
4. Adicione a tag correspondente em `OPENAPI_TAGS` no `app/main.py`

Para injetar a sessão do banco em um endpoint use o `get_db`:

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/example")
async def example(db: Annotated[AsyncSession, Depends(get_db)]):
    ...
```
