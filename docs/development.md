# Desenvolvimento

## Testes

Os testes usam **pytest** com suporte a async via `pytest-asyncio` e cliente HTTP via `httpx`.

```bash
# rodar todos os testes
python3 -m pytest tests/ -v

# rodar com cobertura
python3 -m pytest tests/ -v --cov=app
```

## Linter e formatter

O projeto usa **Ruff** para lint e formatação (substitui flake8, isort e black).

```bash
# verificar
ruff check .

# corrigir automaticamente
ruff check . --fix

# formatar
ruff format .
```

As regras ativas estão configuradas em `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

| Conjunto | Descrição |
|---|---|
| `E` | Erros de estilo PEP 8 |
| `F` | Erros lógicos (pyflakes) |
| `I` | Ordenação de imports (isort) |
| `UP` | Modernização de sintaxe Python (pyupgrade) |

## Adicionando novos endpoints

1. Crie o arquivo em `app/api/v1/routes/nome_do_recurso.py`
2. Defina o `APIRouter` e os endpoints
3. Registre o router em `app/api/v1/router.py`
4. Adicione a tag correspondente em `OPENAPI_TAGS` no `app/main.py`
