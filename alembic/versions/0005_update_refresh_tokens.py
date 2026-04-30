"""update refresh_tokens: hash token, revoked_at, ip_address, user_agent

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # substitui o booleano revoked por um timestamp revoked_at
    op.drop_column("refresh_tokens", "revoked")
    op.add_column(
        "refresh_tokens",
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # contexto da sessão: ip e user-agent
    op.add_column(
        "refresh_tokens",
        sa.Column("ip_address", sa.String(45), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("user_agent", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("refresh_tokens", "user_agent")
    op.drop_column("refresh_tokens", "ip_address")
    op.drop_column("refresh_tokens", "revoked_at")
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "revoked", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
