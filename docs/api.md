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

### `POST /api/v1/auth/login`

Autentica um usuário com email e senha. Retorna um token JWT Bearer.

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

**Erros**

| Código | Motivo |
|---|---|
| `401` | Credenciais inválidas |
| `403` | Usuário inativo |
| `422` | Corpo inválido |

Para detalhes completos sobre o fluxo de autenticação, veja a página [Autenticação](authentication.md).

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
