# GarageHub Backend

API RESTful da plataforma **GarageHub** — sistema de gestão de oficinas mecânicas.

## Stack

- **Python 3.12** + **FastAPI** (ASGI)
- **Pydantic v2** + **pydantic-settings** para validação e configuração
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
│   │   └── exceptions.py     # Handler centralizado de erros
│   └── api/
│       └── v1/
│           ├── router.py
│           └── routes/
│               └── health.py
├── tests/
├── docs/                     # Documentação MkDocs
├── gunicorn.conf.py
├── pyproject.toml
├── Dockerfile
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
| `APP_SECRET_KEY` | `change-me-in-production` | Chave secreta da aplicação |

## Rodando localmente

```bash
fastapi dev app/main.py
```

Com `APP_DEBUG=true` no `.env`:

- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

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
# build
docker build -t garagehub-backend .

# run
docker run -p 8000:8000 --env-file .env garagehub-backend
```

O container sobe com Gunicorn + UvicornWorker em `0.0.0.0:8000`.

## Documentação

```bash
# instalar dependências de dev (inclui mkdocs-material)
pip install -e ".[dev]"

# servir localmente
mkdocs serve
```

Documentação disponível em `http://localhost:8000` (porta padrão do MkDocs).

## Licença

MIT
