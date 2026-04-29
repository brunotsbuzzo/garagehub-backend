# Autenticação

O GarageHub usa **JWT (JSON Web Tokens)** para autenticação stateless. O fluxo é simples: o cliente envia credenciais, recebe um token e o inclui em todas as requisições protegidas.

---

## Fluxo

```
POST /api/v1/auth/login
   │
   ├── valida email + senha no banco
   ├── verifica se o usuário está ativo
   └── retorna access_token (JWT)

Requisições protegidas:
   Authorization: Bearer <access_token>
```

---

## Login

### `POST /api/v1/auth/login`

Autentica um usuário e retorna um token de acesso.

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
  "token_type": "bearer"
}
```

**Erros possíveis**

| Código | Motivo |
|---|---|
| `401` | Email ou senha incorretos |
| `403` | Usuário inativo |
| `422` | Corpo da requisição inválido |

---

## Token JWT

O token é gerado com **PyJWT** e assinado com a chave `APP_SECRET_KEY` usando o algoritmo `HS256`.

**Payload do token:**

```json
{
  "sub": "<uuid-do-usuario>",
  "exp": "<timestamp-de-expiração>"
}
```

A expiração padrão é de **30 minutos**, configurável via `ACCESS_TOKEN_EXPIRE_MINUTES`.

---

## Hashing de senhas

As senhas são armazenadas como hash **bcrypt** via **passlib**. Nunca são armazenadas em texto plano.

```python
from app.core.security import hash_password, verify_password

hashed = hash_password("senha123")
verify_password("senha123", hashed)  # True
```

---

## Criando um usuário (manual / seed)

Ainda não existe endpoint de cadastro. Para criar um usuário diretamente no banco:

```python
from app.core.security import hash_password
from app.models.user import User

user = User(
    email="admin@garagehub.com",
    hashed_password=hash_password("senha-forte"),
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
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do token em minutos |

!!! danger "Produção"
    Defina `APP_SECRET_KEY` com um valor aleatório forte em produção.
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
