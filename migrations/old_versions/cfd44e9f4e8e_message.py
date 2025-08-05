"""message

Revision ID: cfd44e9f4e8e
Revises: 3392d0a63088
Create Date: 2025-07-03 12:53:35.395431

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns


from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'cfd44e9f4e8e'
down_revision: Union[str, Sequence[str], None] = '3392d0a63088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_messages",
        *common_columns(),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("org_conversations.id"), nullable=False),
        sa.Column("content", sa.String(255), nullable=False),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("org_customers.id"), nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=True),
        sa.Column("feedback", sa.String(255), nullable=True),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_messages")
