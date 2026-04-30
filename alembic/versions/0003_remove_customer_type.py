"""remove customer_type

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

customertype_enum = sa.Enum("pessoa_fisica", "pessoa_juridica", name="customertype")


def upgrade() -> None:
    op.drop_column("users", "customer_type")
    customertype_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    customertype_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column(
            "customer_type",
            customertype_enum,
            nullable=False,
            server_default="pessoa_fisica",
        ),
    )
