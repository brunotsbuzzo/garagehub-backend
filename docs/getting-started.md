# Guia de Instalação

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (recomendado para o banco de dados)

## Opção 1 — Docker Compose (recomendado)

A forma mais simples de rodar tudo junto: banco de dados e aplicação.

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd garagehub-backend
```

**2. Configure as variáveis de ambiente**

```bash
cp .env.example .env
```

**3. Suba os serviços**

```bash
docker compose up
```

A API ficará disponível em `http://localhost:8000`.  
Com `APP_DEBUG=true` no `.env`, o Swagger estará em `http://localhost:8000/docs`.

---

## Opção 2 — Instalação local (banco externo)

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd garagehub-backend
```

**2. Crie e ative o virtualenv**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instale as dependências**

```bash
# produção
pip install -e .

# desenvolvimento (inclui pytest, ruff, mkdocs)
pip install -e ".[dev]"
```

**4. Configure as variáveis de ambiente**

```bash
cp .env.example .env
```

Edite o `.env` apontando `DATABASE_URL` para o seu PostgreSQL. Veja a página de [Configuração](configuration.md) para detalhes.

**5. Aplique as migrations**

```bash
alembic upgrade head
```

**6. Inicie o servidor de desenvolvimento**

```bash
fastapi dev app/main.py
```

A API estará disponível em `http://localhost:8000`.

---

!!! tip "Apenas o banco via Docker"
    Se quiser rodar a aplicação localmente mas o banco no Docker:
    ```bash
    docker compose up db
    ```
    Depois inicie a aplicação normalmente com `fastapi dev`.
