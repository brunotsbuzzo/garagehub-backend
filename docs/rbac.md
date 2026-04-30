# Controle de Acesso (RBAC)

O GarageHub usa **Role-Based Access Control (RBAC)** com claims JWT. As permissões são verificadas diretamente no payload do access token, sem consulta extra ao banco — preservando a natureza stateless do JWT.

---

## Papéis (Roles)

Os papéis são definidos no enum `UserRole` em `app/core/enums.py` e armazenados como coluna `role` na tabela `users`.

| Valor no banco | Enum Python | Descrição |
|---|---|---|
| `cliente` | `UserRole.CLIENTE` | Usuário final que solicita serviços na oficina |
| `ajudante` | `UserRole.AJUDANTE` | Auxiliar de apoio geral |
| `ajudante_mecanico` | `UserRole.AJUDANTE_MECANICO` | Auxiliar de mecânica |
| `mecanico` | `UserRole.MECANICO` | Mecânico da equipe |
| `gerente_mecanica` | `UserRole.GERENTE_MECANICA` | Gerente da equipe de mecânica |
| `administrador` | `UserRole.ADMINISTRADOR` | Administrador completo do sistema |

Cada usuário possui **exatamente um** papel. O papel pode ser alterado via `PATCH /api/v1/users/{id}` (requer `user:write`).

---

## Permissões (Permissions)

| Permissão | Descrição |
|---|---|
| `user:read` | Listar e visualizar usuários |
| `user:write` | Criar e editar usuários |
| `user:delete` | Desativar usuários |
| `session:read` | Visualizar sessões ativas |
| `session:write` | Encerrar sessões |

---

## Matriz de permissões por papel

| Permissão | `cliente` | `ajudante` | `ajudante_mecanico` | `mecanico` | `gerente_mecanica` | `administrador` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `session:read`  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `session:write` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `user:read`     | — | — | — | ✓ | ✓ | ✓ |
| `user:write`    | — | — | — | — | ✓ | ✓ |
| `user:delete`   | — | — | — | — | — | ✓ |

---

## Claims no JWT

O access token inclui `roles` e `permissions` no payload:

```json
{
  "sub": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "exp": 1746000000,
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "roles": ["administrador"],
  "permissions": ["user:read", "user:write", "user:delete", "session:read", "session:write"]
}
```

As claims são geradas no momento do login e atualizadas a cada `/auth/refresh` — o que garante que mudanças de papel entrem em vigor na próxima renovação de token.

!!! warning "Mudança imediata de permissão"
    Se uma alteração de papel precisar ter efeito imediato, revogue o access token atual via logout (`POST /auth/logout`) e solicite novo login. O token existente continuará válido até expirar (máx. 30 min) se não for blacklistado.

---

## Verificação nos endpoints

A verificação é feita por dependências FastAPI que leem as claims do JWT. Não há consulta ao banco para checar permissões.

### `require_roles(*roles)`

Exige que o token contenha **pelo menos um** dos papéis listados.

```python
from app.core.deps import require_roles
from app.core.enums import UserRole

@router.get("/gerentes-e-admins")
async def apenas_gerentes(_: User = Depends(require_roles(UserRole.GERENTE_MECANICA, UserRole.ADMINISTRADOR))):
    ...
```

### `require_permissions(*permissions)`

Exige que o token contenha **pelo menos uma** das permissões listadas.

```python
from app.core.deps import require_permissions
from app.core.rbac import Permission

@router.get("/users")
async def list_users(_: User = Depends(require_permissions(Permission.USER_READ))):
    ...
```

---

## Permissões por endpoint

### Auth

| Endpoint | Permissão / Papel |
|---|---|
| `POST /auth/login` | Público |
| `POST /auth/refresh` | Público |
| `POST /auth/logout` | Autenticado |
| `GET /auth/sessions` | Autenticado |
| `DELETE /auth/sessions` | Autenticado |
| `DELETE /auth/sessions/{id}` | Autenticado |

### Users

| Endpoint | Permissão exigida | Papéis que atendem |
|---|---|---|
| `POST /users` | Público | — |
| `GET /users` | `user:read` | `mecanico`, `gerente_mecanica`, `administrador` |
| `GET /users/me` | Autenticado | qualquer |
| `GET /users/{id}` | `user:read` | `mecanico`, `gerente_mecanica`, `administrador` |
| `PATCH /users/me` | Autenticado | qualquer |
| `PATCH /users/{id}` | `user:write` | `gerente_mecanica`, `administrador` |
| `DELETE /users/{id}` | `user:delete` | `administrador` |

---

## Alterando o papel de um usuário

Via API (requer `user:write`):

```bash
curl -X PATCH http://localhost:8000/api/v1/users/<user_id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"role": "mecanico"}'
```

Valores válidos para `role`: `cliente`, `ajudante`, `ajudante_mecanico`, `mecanico`, `gerente_mecanica`, `administrador`.

Via CLI (para criar o primeiro administrador):

```bash
create-superuser --email admin@garagehub.com
```

---

## Guia do desenvolvedor — adicionando roles e permissões

### Adicionando uma nova permissão

**1. Declare a permissão no enum** (`app/core/rbac.py`):

```python
class Permission(str, Enum):
    # ... existentes ...
    VEHICLE_READ  = "vehicle:read"
    VEHICLE_WRITE = "vehicle:write"
```

Use o formato `recurso:ação` para manter consistência.

**2. Atribua a permissão aos papéis relevantes** no `ROLE_PERMISSIONS` do mesmo arquivo:

```python
ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.CLIENTE: frozenset({
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
        Permission.VEHICLE_READ,   # ← clientes podem ver veículos
    }),
    UserRole.MECANICO: frozenset({
        ...
        Permission.VEHICLE_READ,
        Permission.VEHICLE_WRITE,  # ← mecânicos podem editar
    }),
    # ... todos os outros papéis também precisam ser listados
}
```

**3. Use a permissão no endpoint** (`app/api/v1/routes/vehicles.py`):

```python
from app.core.deps import require_permissions
from app.core.rbac import Permission

@router.get("", ...)
async def list_vehicles(_: User = Depends(require_permissions(Permission.VEHICLE_READ))):
    ...
```

Não é necessária nenhuma migration — permissões são resolvidas em código.

---

### Adicionando um novo papel (role)

O papel é um valor do enum `UserRole` armazenado diretamente na coluna `role` da tabela `users`. Adicionar um novo papel envolve código **e** uma migration de banco.

**1. Declare o papel em `app/core/enums.py`** (fonte única de verdade):

```python
class UserRole(str, Enum):
    # ... existentes ...
    INSPETOR = "inspetor"
```

**2. Defina as permissões do novo papel em `app/core/rbac.py`**:

```python
ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    ...
    UserRole.INSPETOR: frozenset({
        Permission.USER_READ,
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
}
```

**3. Crie a migration** para atualizar o tipo enum no PostgreSQL:

```python
# alembic/versions/XXXX_add_inspetor_role.py
def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'inspetor'")

def downgrade() -> None:
    # PostgreSQL não suporta remoção de valores de enum nativamente.
    # A estratégia de downgrade deve recriar o tipo sem o valor.
    pass
```

```bash
alembic upgrade head
```

**Não** é necessário alterar `get_user_roles()` — ela simplesmente retorna `[user.role]`.

---

### Checklist ao adicionar permissão

- [ ] Nova entrada em `Permission` (`app/core/rbac.py`)
- [ ] Atribuída em `ROLE_PERMISSIONS` para os papéis corretos
- [ ] Usada com `require_permissions(...)` no endpoint

### Checklist ao adicionar papel

- [ ] Nova entrada em `UserRole` (`app/core/enums.py`)
- [ ] Mapeamento em `ROLE_PERMISSIONS` (`app/core/rbac.py`)
- [ ] Migration para adicionar o valor ao tipo `userrole` no PostgreSQL
- [ ] Migration aplicada (`alembic upgrade head`)

---

## Considerações de segurança

- O payload JWT é **assinado** (HS256), não criptografado — não inclua dados sensíveis nas claims.
- Roles e permissões são incluídos no token no momento da emissão. Mudanças só refletem no próximo login ou refresh.
- Para revogação imediata após mudança de papel crítica: blackliste o token via logout (`POST /auth/logout`).
- O tamanho do token aumenta com o número de claims. Mantenha as listas de permissões concisas.
