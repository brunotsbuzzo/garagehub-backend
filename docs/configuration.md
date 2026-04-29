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

## Exemplo de `.env`

```dotenv
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=change-me-in-production
```

!!! warning "Produção"
    Nunca defina `APP_DEBUG=true` em produção. O Swagger UI e ReDoc ficam desabilitados quando `APP_DEBUG=false`.

!!! danger "Secret Key"
    Troque `APP_SECRET_KEY` por um valor aleatório forte em produção. O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.
