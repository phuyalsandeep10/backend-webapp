"""attachement

Revision ID: 0551e46b3c51
Revises: 303db920ef84
Create Date: 2025-07-27 08:10:16.104860

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0551e46b3c51'
down_revision: Union[str, Sequence[str], None] = '303db920ef84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("org_message_attachments", sa.Column("file_url", sa.String(), nullable=True))
    op.add_column("org_message_attachments", sa.Column("file_size", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("org_message_attachments", "file_size")
    op.drop_column("org_message_attachments", "file_url")
