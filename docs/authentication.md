# Autenticação

O GarageHub usa **JWT** para access tokens e **refresh tokens** persistidos em banco para gestão de sessão. O fluxo é stateless para requisições normais e stateful apenas para renovação e revogação de sessão.

---

## Visão geral

```
POST /auth/login
  ├── valida credenciais
  ├── revoga sessões ativas do mesmo dispositivo (ip + user_agent)
  ├── limita sessões simultâneas (máx. MAX_ACTIVE_SESSIONS, default 5)
  └── emite access_token (JWT) + refresh_token

Requisição protegida:
  Authorization: Bearer <access_token>
  ├── verifica assinatura e expiração do JWT
  └── verifica JTI na tabela blacklisted_tokens

POST /auth/refresh
  ├── valida refresh_token (hash SHA-256 no banco)
  ├── revoga o token atual (revoked_at = now())
  └── emite novo par (rotação obrigatória)

POST /auth/logout
  ├── revoga o refresh_token
  └── adiciona JTI do access_token à blacklist

DELETE /auth/sessions
  ├── revoga TODOS os refresh_tokens do usuário
  └── adiciona JTI do access_token atual à blacklist

DELETE /auth/sessions/{id}
  └── revoga sessão específica pelo ID
```

---

## Tokens

| Token | Tipo | Duração | Armazenamento |
|---|---|---|---|
| **access_token** | JWT HS256 com `jti` | 30 min | Apenas no cliente |
| **refresh_token** | String aleatória | 30 dias | SHA-256 no banco |

O access token carrega um `jti` (JWT ID, UUID v4) que permite revogação individual via blacklist. O refresh token é armazenado como hash SHA-256 — o valor bruto nunca é persistido.

---

## Endpoints

### `POST /api/v1/auth/login`

Autentica o usuário. Antes de emitir os tokens, o sistema:

1. Valida e-mail e senha
2. Revoga sessões ativas do mesmo dispositivo (`ip_address` + `user_agent`)
3. Verifica se o limite de `MAX_ACTIVE_SESSIONS` foi atingido; se sim, revoga as sessões mais antigas
4. Cria nova sessão registrando `ip_address`, `user_agent` e `expires_at`

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
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4...",
    "expires_in": 1800
  },
  "quantity": 1,
  "message": "Login realizado com sucesso.",
  "status_code": 200
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

Valida o refresh token, revoga-o e emite novo par (rotação obrigatória). Registra `ip_address` e `user_agent` da nova sessão.

**Lógica do servidor:**

1. Calcula SHA-256 do `refresh_token` recebido e localiza no banco
2. Verifica `revoked_at` (nulo = ativo) e `expires_at`
3. Marca o token atual com `revoked_at = now()`
4. Gera novo access token (JWT com novo `jti`) e novo refresh token
5. Armazena o hash do novo refresh token

**Corpo da requisição**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4..."
}
```

**Resposta `200 OK`** — mesmo envelope do login com novo par de tokens

**Erros**

| Código | Motivo |
|---|---|
| `401` | Refresh token inválido, expirado ou já revogado |

---

### `POST /api/v1/auth/logout`

Requer autenticação. Revoga o refresh token informado e adiciona o `jti` do access token atual à blacklist para revogação imediata.

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
| `401` | Access token inválido/expirado ou refresh token inválido |

---

### `GET /api/v1/auth/sessions`

Requer autenticação. Lista todas as sessões ativas do usuário autenticado.

**Resposta `200 OK`**

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0 ...",
    "created_at": "2026-04-30T12:00:00Z",
    "expires_at": "2026-05-30T12:00:00Z"
  }
]
```

---

### `DELETE /api/v1/auth/sessions`

Requer autenticação. Revoga **todas** as sessões ativas do usuário e blacklista o access token atual.

**Resposta `204 No Content`**

---

### `DELETE /api/v1/auth/sessions/{session_id}`

Requer autenticação. Revoga uma sessão específica pelo ID. O usuário só pode revogar suas próprias sessões.

**Resposta `204 No Content`**

**Erros**

| Código | Motivo |
|---|---|
| `404` | Sessão não encontrada |
| `409` | Sessão já encerrada |

---

## Rotas protegidas

Inclua o access token no header `Authorization`:

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

Em cada requisição protegida, o sistema verifica:

1. Assinatura e expiração do JWT
2. Se o `jti` está na tabela `blacklisted_tokens`

Há dois níveis de proteção:

| Dependência | Requisito |
|---|---|
| `get_current_user` | Token válido + não blacklisted + usuário ativo |
| `get_current_admin` | Tudo acima + `is_admin = true` |

---

## Gerenciamento de sessões

### Múltiplos dispositivos

Cada dispositivo mantém seu próprio refresh token. O banco identifica sessões por `ip_address` + `user_agent`.

### Limite de sessões simultâneas

Configurável via `MAX_ACTIVE_SESSIONS` (padrão: `5`). No login, se o limite for atingido, as sessões mais antigas são revogadas automaticamente para abrir espaço.

### Login no mesmo dispositivo

Se o usuário fizer login em um dispositivo que já possui uma sessão ativa (mesmo `ip_address` + `user_agent`), a sessão anterior é revogada antes de criar a nova.

---

## Blacklist de access tokens

Embora os access tokens sejam de curta duração (30 min), situações que exigem revogação imediata utilizam a tabela `blacklisted_tokens`:

| Situação | Comportamento |
|---|---|
| `POST /auth/logout` | Blacklista o `jti` do token atual |
| `DELETE /auth/sessions` | Blacklista o `jti` do token atual + revoga todas as sessões |

A entrada na blacklist é criada com `expires_at = now() + ACCESS_TOKEN_EXPIRE_MINUTES`, permitindo limpeza automática de entradas expiradas.

---

## Rotação de refresh token

A cada `/auth/refresh`, o token anterior recebe `revoked_at = now()` e um novo par é emitido. Isso garante uso único por token e permite detecção de replay attacks: se um token for interceptado e usado por um atacante, o uso do token original pelo usuário legítimo falhará (pois já foi revogado).

---

## Hash do refresh token

```
token_bruto = secrets.token_urlsafe(48)   ← retornado ao cliente
token_hash  = SHA-256(token_bruto)        ← armazenado no banco

verificação: SHA-256(token_recebido) == token_hash
```

Mesmo com acesso direto ao banco, não é possível reconstituir o token original.

---

## Criando um usuário

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "cliente@garagehub.com", "password": "senha-forte"}'
```

Para criar o primeiro administrador:

```bash
create-superuser
```

---

## Configurações relacionadas

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_SECRET_KEY` | `change-me-in-production` | Chave de assinatura do JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do access token em minutos |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Validade do refresh token em dias |
| `MAX_ACTIVE_SESSIONS` | `5` | Máximo de sessões simultâneas por usuário |

!!! danger "Produção"
    Defina `APP_SECRET_KEY` com um valor aleatório forte em produção.
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
