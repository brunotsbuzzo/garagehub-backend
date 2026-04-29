# Deploy

## Docker

**Build da imagem**

```bash
docker build -t garagehub-backend .
```

**Rodar o container**

```bash
docker run -p 8000:8000 --env-file .env garagehub-backend
```

O servidor inicia com **Gunicorn + UvicornWorker** (ASGI), configurado para 2 workers na porta 8000.

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
