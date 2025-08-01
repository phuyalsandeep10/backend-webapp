"""message attachments

Revision ID: d1a4b37f9381
Revises: cfd44e9f4e8e
Create Date: 2025-07-03 12:56:13.242856

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa
from migrations.common import common_columns



# revision identifiers, used by Alembic.
revision: str = 'd1a4b37f9381'
down_revision: Union[str, Sequence[str], None] = 'cfd44e9f4e8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_message_attachments",
        *common_columns(),
        sa.Column("message_id", sa.Integer, sa.ForeignKey("org_messages.id"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_message_attachments")
