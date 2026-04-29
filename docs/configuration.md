# Configuração

As configurações são carregadas via variáveis de ambiente ou arquivo `.env` na raiz do projeto, gerenciadas pelo **pydantic-settings**.

## Variáveis disponíveis

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `APP_ENV` | `str` | `development` | Ambiente de execução (`development`, `production`) |
| `APP_DEBUG` | `bool` | `false` | Habilita modo debug e expõe `/docs` e `/redoc` |
| `APP_SECRET_KEY` | `str` | `change-me-in-production` | Chave secreta da aplicação |
| `API_V1_PREFIX` | `str` | `/api/v1` | Prefixo de todas as rotas v1 |
| `PROJECT_NAME` | `str` | `GarageHub API` | Nome exibido no Swagger |
| `PROJECT_VERSION` | `str` | `0.1.0` | Versão exibida no Swagger |
| `DATABASE_URL` | `str` | `postgresql+asyncpg://garagehub:garagehub@localhost:5432/garagehub` | URL de conexão com o PostgreSQL |

## Exemplo de `.env`

```dotenv
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=change-me-in-production

DATABASE_URL=postgresql+asyncpg://garagehub:garagehub@localhost:5432/garagehub
```

## Formato da DATABASE_URL

O driver utilizado é `asyncpg`, portanto a URL **deve** usar o prefixo `postgresql+asyncpg://`:

```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

Quando rodando com Docker Compose, o host é o nome do serviço definido no `docker-compose.yml` (`db`):

```dotenv
DATABASE_URL=postgresql+asyncpg://garagehub:garagehub@db:5432/garagehub
```

!!! warning "Produção"
    Nunca defina `APP_DEBUG=true` em produção. O Swagger UI e ReDoc ficam desabilitados quando `APP_DEBUG=false`.

!!! danger "Segredos"
    Troque `APP_SECRET_KEY` e as credenciais do banco por valores fortes em produção. O arquivo `.env` está no `.gitignore` e **nunca deve ser commitado**.
