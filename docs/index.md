# GarageHub API

API backend da plataforma **GarageHub** — sistema de gestão de oficinas mecânicas.

## Visão geral

O GarageHub Backend é uma API RESTful construída com **FastAPI** e **Python 3.12**, seguindo os princípios de Clean Architecture e boas práticas de desenvolvimento moderno.

## Stack

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12 | Linguagem |
| FastAPI | ≥ 0.115 | Framework web ASGI |
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
│   │   └── exceptions.py     # Handler centralizado de erros
│   └── api/
│       └── v1/
│           ├── router.py     # Agrega todas as rotas v1
│           └── routes/
│               └── health.py
├── tests/
│   └── test_health.py
├── docs/                     # Esta documentação
├── gunicorn.conf.py          # Configuração do servidor de produção
├── pyproject.toml            # Dependências e ferramentas
├── Dockerfile
└── .env.example
```
