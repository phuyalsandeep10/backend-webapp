"""2fa_support

Revision ID: dccc09a8929f
Revises: 6aeb44fec6af
Create Date: 2025-07-16 16:28:25.837651

"""

from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dccc09a8929f"
down_revision: Union[str, Sequence[str], None] = "6aeb44fec6af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sys_users",
        sa.Column(
            "two_fa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )

    op.add_column(
        "sys_users", sa.Column("two_fa_secret", sa.String(length=255), nullable=True)
    )

    op.add_column(
        "sys_users", sa.Column("two_fa_auth_url", sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("sys_users", "two_fa_enabled")
    op.drop_column("sys_users", "two_fa_secret")
    op.drop_column("sys_users", "two_fa_auth_url")
