# GarageHub API

API backend da plataforma **GarageHub** — sistema de gestão de oficinas mecânicas.

## Visão geral

O GarageHub Backend é uma API RESTful construída com **FastAPI** e **Python 3.12**, seguindo as melhores práticas de desenvolvimento moderno: banco de dados async, migrations versionadas, configuração por variáveis de ambiente e servidor de produção com Gunicorn.

## Stack

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12 | Linguagem |
| FastAPI | ≥ 0.115 | Framework web ASGI |
| SQLAlchemy | ≥ 2.0 | ORM async |
| asyncpg | ≥ 0.30 | Driver async para PostgreSQL |
| Alembic | ≥ 1.14 | Migrations |
| PostgreSQL | 16 | Banco de dados |
| Pydantic v2 | ≥ 2.0 | Validação e serialização |
| pydantic-settings | ≥ 2.6 | Gerenciamento de configuração |
| Gunicorn + Uvicorn | ≥ 23.0 | Servidor de produção |
| Ruff | ≥ 0.8 | Linter e formatter |
| pytest | ≥ 8.0 | Testes |

## Estrutura do projeto

```
garagehub-backend/
├── app/
│   ├── main.py               # App factory + lifespan
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── database.py       # Engine async, sessão e get_db
│   │   └── exceptions.py     # Handler centralizado de erros
│   ├── models/
│   │   └── base.py           # Base declarativa + mixins
│   └── api/
│       └── v1/
│           ├── router.py     # Agrega todas as rotas v1
│           └── routes/
│               └── health.py
├── alembic/                  # Migrations versionadas
│   ├── env.py                # Setup async do Alembic
│   └── versions/
├── tests/
│   └── test_health.py
├── docs/                     # Esta documentação
├── alembic.ini
├── gunicorn.conf.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```
