# Endpoints

Todas as rotas estão sob o prefixo `/api/v1`.

A documentação interativa completa está disponível via Swagger UI em `/docs` (requer `APP_DEBUG=true`).

---

## Health

### `GET /api/v1/health`

Verifica se a API está disponível e aceitando requisições.

**Resposta `200 OK`**

```json
{
  "status": "ok"
}
```

---

## Auth

Para detalhes completos sobre o fluxo, tokens e segurança, veja a página [Autenticação](authentication.md).

### `POST /api/v1/auth/login`

Autentica o usuário e retorna access token e refresh token.

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
| `401` | Credenciais inválidas |
| `403` | Usuário inativo |
| `422` | Corpo inválido |

---

### `POST /api/v1/auth/refresh`

Emite um novo par de tokens. O refresh token utilizado é revogado (rotação automática).

**Corpo da requisição**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHNlY3VyZSByYW5kb20gdG9rZW4..."
}
```

**Resposta `200 OK`** — novo `access_token` + novo `refresh_token` (mesmo envelope de login)

**Erros**

| Código | Motivo |
|---|---|
| `401` | Refresh token inválido, expirado ou já revogado |

---

### `POST /api/v1/auth/logout`

Revoga o refresh token, encerrando a sessão.

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

## Users

Endpoints para gerenciamento de usuários. O objeto de resposta `UserResponse` segue o formato:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "cliente@garagehub.com",
  "is_active": true,
  "cpf": "123.456.789-09",
  "cnpj": null,
  "customer_type": "pessoa_fisica",
  "is_admin": false,
  "is_team_member": false
}
```

---

### `POST /api/v1/users`

Cria um novo usuário. Não requer autenticação.

**Corpo da requisição**

```json
{
  "email": "cliente@garagehub.com",
  "password": "senha123",
  "cpf": "123.456.789-09",
  "customer_type": "pessoa_fisica"
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `email` | string | Sim | E-mail válido e único |
| `password` | string | Sim | Senha em texto plano (será hasheada) |
| `cpf` | string | Não | CPF do usuário (pessoa física) |
| `cnpj` | string | Não | CNPJ da empresa (pessoa jurídica) |
| `customer_type` | string | Não | `pessoa_fisica` (padrão) ou `pessoa_juridica` |

**Resposta `201 Created`** — `UserResponse`

**Erros**

| Código | Motivo |
|---|---|
| `409` | E-mail já cadastrado |
| `422` | Corpo inválido |

---

### `GET /api/v1/users`

Lista todos os usuários com paginação. Requer perfil de **administrador**.

**Query params**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `skip` | integer | `0` | Registros a pular |
| `limit` | integer | `50` | Máximo de registros (1–100) |

**Resposta `200 OK`** — `list[UserResponse]`

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente ou inválido |
| `403` | Usuário não é administrador |

---

### `GET /api/v1/users/me`

Retorna os dados do usuário autenticado. Requer token Bearer.

**Resposta `200 OK`** — `UserResponse`

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente, inválido ou expirado |
| `403` | Usuário inativo |

---

### `GET /api/v1/users/{user_id}`

Retorna os dados de um usuário pelo UUID. Requer perfil de **administrador**.

**Path param:** `user_id` — UUID do usuário.

**Resposta `200 OK`** — `UserResponse`

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente ou inválido |
| `403` | Usuário não é administrador |
| `404` | Usuário não encontrado |

---

### `PATCH /api/v1/users/me`

Atualiza os dados do usuário autenticado. Todos os campos são opcionais. Requer token Bearer.

**Corpo da requisição**

```json
{
  "cpf": "123.456.789-09",
  "cnpj": null,
  "customer_type": "pessoa_fisica"
}
```

**Resposta `200 OK`** — `UserResponse`

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente, inválido ou expirado |
| `403` | Usuário inativo |
| `422` | Corpo inválido |

---

### `PATCH /api/v1/users/{user_id}`

Atualiza os dados de qualquer usuário. Requer perfil de **administrador**.

Além dos campos de `PATCH /users/me`, permite alterar flags de acesso:

```json
{
  "is_active": false,
  "is_admin": true,
  "is_team_member": false
}
```

**Resposta `200 OK`** — `UserResponse`

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente ou inválido |
| `403` | Usuário não é administrador |
| `404` | Usuário não encontrado |
| `422` | Corpo inválido |

---

### `DELETE /api/v1/users/{user_id}`

Desativa um usuário (soft delete — seta `is_active = false`). Requer perfil de **administrador**.

**Path param:** `user_id` — UUID do usuário.

**Resposta `204 No Content`**

**Erros**

| Código | Motivo |
|---|---|
| `401` | Token ausente ou inválido |
| `403` | Usuário não é administrador |
| `404` | Usuário não encontrado |

---

## Erros

Todos os erros gerados pela aplicação seguem o formato padrão:

```json
{
  "detail": "Mensagem descritiva do erro."
}
```

| Código | Significado |
|---|---|
| `400` | Requisição inválida |
| `401` | Não autenticado |
| `403` | Sem permissão |
| `404` | Recurso não encontrado |
| `422` | Erro de validação (Pydantic) |
| `500` | Erro interno do servidor |
