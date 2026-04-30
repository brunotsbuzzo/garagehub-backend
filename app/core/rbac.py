from enum import Enum
from typing import TYPE_CHECKING

from app.core.enums import UserRole

if TYPE_CHECKING:
    from app.models.user import User


class Permission(str, Enum):
    USER_READ    = "user:read"
    USER_WRITE   = "user:write"
    USER_DELETE  = "user:delete"
    SESSION_READ  = "session:read"
    SESSION_WRITE = "session:write"


# Matriz de permissões por papel
# Quanto mais alto na hierarquia, mais permissões acumula.
ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.CLIENTE: frozenset({
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
    UserRole.AJUDANTE: frozenset({
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
    UserRole.AJUDANTE_MECANICO: frozenset({
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
    UserRole.MECANICO: frozenset({
        Permission.USER_READ,
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
    UserRole.GERENTE_MECANICA: frozenset({
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
    UserRole.ADMINISTRADOR: frozenset({
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.SESSION_READ,
        Permission.SESSION_WRITE,
    }),
}


def get_user_roles(user: "User") -> list[UserRole]:
    return [user.role]


def get_user_permissions(roles: list[UserRole]) -> list[Permission]:
    perms: set[Permission] = set()
    for role in roles:
        perms.update(ROLE_PERMISSIONS.get(role, frozenset()))
    return list(perms)
