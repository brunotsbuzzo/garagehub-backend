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
│   │   ├── deps.py           # Dependências JWT (get_current_user, get_current_admin)
│   │   ├── exceptions.py     # Handler centralizado de erros
│   │   └── security.py       # JWT + hashing de senhas
│   ├── models/
│   │   ├── base.py           # Base declarativa + UUIDMixin + TimestampMixin
│   │   └── user.py           # Model de usuário
│   ├── schemas/
│   │   ├── auth.py           # Schemas de login e token
│   │   └── user.py           # UserResponse, UserCreate, UserUpdate, UserAdminUpdate
│   ├── services/
│   │   ├── auth.py           # Lógica de autenticação
│   │   └── user.py           # CRUD de usuários
│   └── api/
│       └── v1/
│           ├── router.py
│           └── routes/
│               ├── health.py
│               ├── auth.py   # POST /auth/login
│               └── users.py  # CRUD /users
├── alembic/                  # Migrations
│   ├── env.py
│   └── versions/
│       ├── 0001_create_users_table.py
│       └── 0002_add_user_profile_fields.py
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

## Endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/health` | — | Health check |
| `POST` | `/api/v1/auth/login` | — | Login (retorna JWT) |
| `POST` | `/api/v1/users` | — | Criar usuário |
| `GET` | `/api/v1/users` | Admin | Listar usuários |
| `GET` | `/api/v1/users/me` | Token | Dados do usuário logado |
| `GET` | `/api/v1/users/{id}` | Admin | Buscar usuário por ID |
| `PATCH` | `/api/v1/users/me` | Token | Atualizar próprio perfil |
| `PATCH` | `/api/v1/users/{id}` | Admin | Atualizar qualquer usuário |
| `DELETE` | `/api/v1/users/{id}` | Admin | Desativar usuário (soft delete) |

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

Use o token nas rotas protegidas:

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

## Usuários

Crie um novo usuário via API:

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123", "customer_type": "pessoa_fisica"}'
```

## Superusuário

Cria o usuário root administrador do sistema, com `is_admin = true`. Similar ao `createsuperuser` do Django.

**Modo interativo (recomendado):**

```bash
create-superuser
```

```
E-mail: admin@garagehub.com
Senha:
Confirme a senha:
Superusuário criado com sucesso.
  E-mail : admin@garagehub.com
  ID     : 3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**Passando o e-mail via flag** (senha solicitada com segurança no prompt):

```bash
create-superuser --email admin@garagehub.com
```

**Modo não-interativo** (para scripts de seed e CI):

```bash
create-superuser --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD"
```

> **Atenção:** passar `--password` em linha de comando expõe a senha no histórico do shell. Prefira variáveis de ambiente ou o modo interativo em produção.

**Via Docker:**

```bash
docker compose exec app create-superuser --email admin@garagehub.com
```

**Validações aplicadas:**

- E-mail deve ser único no banco
- Senha com no mínimo 8 caracteres
- No modo interativo, a senha é confirmada antes de salvar

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
