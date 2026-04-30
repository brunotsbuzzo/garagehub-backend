"""add role column to users, drop is_admin and is_team_member

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

userrole_enum = sa.Enum(
    "cliente",
    "ajudante",
    "ajudante_mecanico",
    "mecanico",
    "gerente_mecanica",
    "administrador",
    name="userrole",
)


def upgrade() -> None:
    userrole_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            userrole_enum,
            nullable=False,
            server_default="cliente",
        ),
    )

    # Data migration: promote existing admins and team members to the closest role
    op.execute(
        "UPDATE users SET role = 'administrador' WHERE is_admin = true"
    )
    op.execute(
        "UPDATE users SET role = 'mecanico' WHERE is_admin = false AND is_team_member = true"
    )

    op.drop_column("users", "is_admin")
    op.drop_column("users", "is_team_member")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_team_member", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.execute(
        "UPDATE users SET is_admin = true WHERE role = 'administrador'"
    )
    op.execute(
        "UPDATE users SET is_team_member = true "
        "WHERE role IN ('mecanico', 'ajudante_mecanico', 'ajudante', 'gerente_mecanica')"
    )

    op.drop_column("users", "role")
    userrole_enum.drop(op.get_bind(), checkfirst=True)
