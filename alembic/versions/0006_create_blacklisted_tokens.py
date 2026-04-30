"""create blacklisted_tokens table

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "blacklisted_tokens",
        sa.Column("jti", sa.String(36), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index("ix_blacklisted_tokens_user_id", "blacklisted_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_blacklisted_tokens_user_id", table_name="blacklisted_tokens")
    op.drop_table("blacklisted_tokens")
