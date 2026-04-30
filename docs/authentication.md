# Autenticação

O GarageHub usa **JWT** para access tokens e **refresh tokens** persistidos em banco para gestão de sessão. O fluxo é stateless para requisições normais e stateful apenas para renovação e revogação de sessão.

---

## Visão geral

```
┌─────────┐        POST /auth/login         ┌─────────┐
│ Cliente │ ──────────────────────────────▶ │   API   │
│         │ ◀────────────────────────────── │         │
│         │   access_token + refresh_token  │         │
│         │                                 │         │
│         │   GET /api/v1/users/me          │         │
│         │   Authorization: Bearer <jwt>   │         │
│         │ ──────────────────────────────▶ │         │
│         │ ◀────────────────────────────── │         │
│         │          200 OK                 │         │
│         │                                 │         │
│         │   POST /auth/refresh            │         │
│         │   { refresh_token }             │         │
│         │ ──────────────────────────────▶ │         │
│         │ ◀────────────────────────────── │         │
│         │   novo access_token + refresh   │         │
│         │                                 │         │
│         │   POST /auth/logout             │         │
│         │   { refresh_token }             │         │
│         │ ──────────────────────────────▶ │         │
│         │ ◀────────────────────────────── │         │
└─────────┘          204 No Content         └─────────┘
```

---

## Tokens

| Token | Tipo | Duração | Armazenamento |
|---|---|---|---|
| **access_token** | JWT (HS256) | 30 min | Apenas no cliente |
| **refresh_token** | String aleatória | 30 dias | Banco de dados |

O access token é stateless — validado apenas pela assinatura JWT, sem consulta ao banco. O refresh token é verificado no banco a cada uso e pode ser revogado a qualquer momento.

---

## Endpoints

### `POST /api/v1/auth/login`

Autentica o usuário e retorna os dois tokens.

**Corpo da requisição**

```json
{
  "email": "mecanico@garagehub.com",
  "password": "senha123"
}
```

**Resposta `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4...",
  "token_type": "bearer"
}
```

**Erros**

| Código | Motivo |
|---|---|
| `401` | Email ou senha incorretos |
| `403` | Usuário inativo |
| `422` | Corpo inválido |

---

### `POST /api/v1/auth/refresh`

Emite um novo par de tokens a partir de um refresh token válido. O token utilizado é **revogado automaticamente** (rotação de token).

**Corpo da requisição**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4..."
}
```

**Resposta `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "bm93IHlvdSBoYXZlIGEgbmV3IHJlZnJlc2gudG9r...",
  "token_type": "bearer"
}
```

**Erros**

| Código | Motivo |
|---|---|
| `401` | Refresh token inválido, expirado ou já revogado |

---

### `POST /api/v1/auth/logout`

Revoga o refresh token, encerrando a sessão. O access token corrente expira naturalmente no prazo de 30 minutos.

**Corpo da requisição**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4..."
}
```

**Resposta `204 No Content`**

**Erros**

| Código | Motivo |
|---|---|
| `401` | Refresh token inválido ou já revogado |

---

## Rotas protegidas

Inclua o access token no header `Authorization` de todas as requisições protegidas:

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

Há dois níveis de proteção:

| Dependência | Requisito |
|---|---|
| `get_current_user` | Token válido + usuário ativo |
| `get_current_admin` | Token válido + usuário ativo + `is_admin = true` |

---

## Payload do JWT

```json
{
  "sub": "<uuid-do-usuario>",
  "exp": "<unix-timestamp-de-expiração>"
}
```

O token é assinado com `APP_SECRET_KEY` usando `HS256`.

---

## Rotação de refresh token

A cada chamada a `/auth/refresh`, o token antigo é **revogado** e um novo é emitido. Isso limita a janela de uso de um token roubado: assim que o usuário legítimo renova, o token comprometido deixa de funcionar.

---

## Criando um usuário

Use o endpoint público de cadastro:

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "cliente@garagehub.com", "password": "senha-forte"}'
```

Para criar o primeiro administrador do sistema, use o comando CLI:

```bash
create-superuser
# E-mail: admin@garagehub.com
# Senha: ••••••••
# Confirme a senha: ••••••••
# Superusuário criado com sucesso.
```

Para promover um usuário existente a administrador, use `PATCH /api/v1/users/{user_id}` com `"is_admin": true`, ou diretamente no banco:

```python
from app.core.security import hash_password
from app.models.user import User

user = User(
    email="admin@garagehub.com",
    hashed_password=hash_password("senha-forte"),
    is_admin=True,
)
session.add(user)
await session.commit()
```

---

## Configurações relacionadas

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_SECRET_KEY` | `change-me-in-production` | Chave de assinatura do JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do access token em minutos |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Validade do refresh token em dias |

!!! danger "Produção"
    Defina `APP_SECRET_KEY` com um valor aleatório forte em produção.
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
