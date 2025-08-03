"""refreshtoken

Revision ID: 6bbd80a33f72
Revises: 71773e73c420
Create Date: 2025-06-25 09:36:05.642180

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

from migrations.common import common_columns

# revision identifiers, used by Alembic.
revision: str = "6bbd80a33f72"
down_revision: Union[str, Sequence[str], None] = "71773e73c420"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_tokens",
        *common_columns(),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=False),
        sa.Column("token", sa.String, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("refresh_tokens")
