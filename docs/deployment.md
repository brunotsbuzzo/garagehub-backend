# Deploy

## Docker Compose (recomendado)

O `docker-compose.yml` orquestra a aplicação e o banco de dados juntos.

```bash
# subir tudo
docker compose up

# subir em background
docker compose up -d

# derrubar tudo
docker compose down

# derrubar e apagar os dados do banco
docker compose down -v
```

### Serviços

| Serviço | Imagem | Porta | Descrição |
|---|---|---|---|
| `db` | `postgres:16-alpine` | `5432` | Banco de dados PostgreSQL |
| `app` | build local | `8000` | API GarageHub |

O serviço `app` só inicia após o `db` estar saudável (`healthcheck` configurado no `docker-compose.yml`).

### Migrations com Docker Compose

```bash
# aplicar migrations no banco do compose
docker compose exec app alembic upgrade head
```

---

## Docker (imagem isolada)

**Build da imagem**

```bash
docker build -t garagehub-backend .
```

**Rodar o container**

```bash
docker run -p 8000:8000 --env-file .env garagehub-backend
```

O servidor inicia com **Gunicorn + UvicornWorker** (ASGI), configurado para 2 workers na porta 8000.

---

## Gunicorn (sem Docker)

As configurações do servidor estão em `gunicorn.conf.py`:

```python
worker_class = "uvicorn.workers.UvicornWorker"
workers = 2
bind = "0.0.0.0:8000"
accesslog = "-"
errorlog = "-"
```

Para iniciar manualmente:

```bash
gunicorn app.main:app
```

!!! tip "Número de workers"
    A regra geral para produção é `2 * CPUs + 1`. Ajuste o valor de `workers` em `gunicorn.conf.py` conforme o hardware disponível.

!!! warning "Variáveis de ambiente em produção"
    Passe as variáveis via `--env-file` no Docker ou via secrets do seu provedor de cloud. Nunca comite o `.env` de produção.

---

## Migrations em produção

Execute as migrations **antes** de subir a nova versão da aplicação:

```bash
alembic upgrade head
```

Para verificar o estado atual:

```bash
alembic current
alembic history
```
