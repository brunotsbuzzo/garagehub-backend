# GarageHub Backend

API RESTful da plataforma **GarageHub** — sistema de gestão de oficinas mecânicas.

## Stack

- **Python 3.12** + **FastAPI** (ASGI)
- **SQLAlchemy 2.0 async** + **asyncpg** para banco de dados
- **Alembic** para migrations
- **PostgreSQL 16** como banco de dados
- **Pydantic v2** + **pydantic-settings** para validação e configuração
- **PyJWT** + **passlib/bcrypt** para autenticação JWT
- **Gunicorn + Uvicorn** em produção
- **Ruff** para lint e formatação
- **pytest + httpx** para testes

## Estrutura

```
garagehub-backend/
├── app/
│   ├── main.py               # App factory + lifespan
│   ├── core/
│   │   ├── config.py         # Settings via pydantic-settings
│   │   ├── database.py       # Engine async + sessão + get_db
│   │   ├── exceptions.py     # Handler centralizado de erros
│   │   └── security.py       # JWT + hashing de senhas
│   ├── models/
│   │   ├── base.py           # Base declarativa + UUIDMixin + TimestampMixin
│   │   └── user.py           # Model de usuário
│   ├── schemas/
│   │   └── auth.py           # Schemas de login e token
│   ├── services/
│   │   └── auth.py           # Lógica de autenticação
│   └── api/
│       └── v1/
│           ├── router.py
│           └── routes/
│               ├── health.py
│               └── auth.py   # POST /auth/login
├── alembic/                  # Migrations
│   ├── env.py
│   └── versions/
│       └── 0001_create_users_table.py
├── tests/
├── docs/                     # Documentação MkDocs
├── alembic.ini
├── gunicorn.conf.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## Instalação

```bash
# 1. crie o virtualenv
python3 -m venv .venv && source .venv/bin/activate

# 2. instale as dependências
pip install -e ".[dev]"

# 3. configure o ambiente
cp .env.example .env
```

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `development` | Ambiente de execução |
| `APP_DEBUG` | `false` | Habilita `/docs` e `/redoc` |
| `APP_SECRET_KEY` | `change-me-in-production` | Chave de assinatura dos tokens JWT |
| `DATABASE_URL` | `postgresql+asyncpg://garagehub:garagehub@localhost:5432/garagehub` | URL de conexão com o banco |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do token de acesso em minutos |

## Rodando localmente

**Com Docker Compose (recomendado):**

```bash
docker compose up
```

Sobe o banco de dados e a aplicação juntos. A API ficará disponível em `http://localhost:8000`.

**Sem Docker (banco externo):**

```bash
fastapi dev app/main.py
```

Com `APP_DEBUG=true` no `.env`:

- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

## Migrations

```bash
# aplicar todas as migrations
alembic upgrade head

# criar nova migration após adicionar/alterar um model
alembic revision --autogenerate -m "descricao"

# desfazer a última migration
alembic downgrade -1
```

## Autenticação

O login é feito via `POST /api/v1/auth/login` com email e senha. A resposta inclui um token JWT Bearer.

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Testes

```bash
python3 -m pytest tests/ -v
```

## Lint

```bash
ruff check . --fix && ruff format .
```

## Docker

```bash
# subir tudo (app + banco)
docker compose up

# apenas o banco (para rodar a app localmente)
docker compose up db
```

## Documentação

```bash
mkdocs serve
# acesse http://localhost:8000
```

## Licença

MIT
