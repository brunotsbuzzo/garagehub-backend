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
