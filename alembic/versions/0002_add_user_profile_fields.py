"""add user profile fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

customertype_enum = sa.Enum("pessoa_fisica", "pessoa_juridica", name="customertype")


def upgrade() -> None:
    customertype_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("cpf", sa.String(14), nullable=True))
    op.add_column("users", sa.Column("cnpj", sa.String(18), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "customer_type",
            customertype_enum,
            nullable=False,
            server_default="pessoa_fisica",
        ),
    )
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("is_team_member", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_team_member")
    op.drop_column("users", "is_admin")
    op.drop_column("users", "customer_type")
    op.drop_column("users", "cnpj")
    op.drop_column("users", "cpf")

    customertype_enum.drop(op.get_bind(), checkfirst=True)
