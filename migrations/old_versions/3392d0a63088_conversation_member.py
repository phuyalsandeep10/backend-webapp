"""conversation member

Revision ID: 3392d0a63088
Revises: 70f105b2b468
Create Date: 2025-07-03 12:50:55.937287

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa
from migrations.common import common_columns

# revision identifiers, used by Alembic.
revision: str = '3392d0a63088'
down_revision: Union[str, Sequence[str], None] = '70f105b2b468'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_conversation_members",
        *common_columns(),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("org_conversations.id"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_conversation_members")
