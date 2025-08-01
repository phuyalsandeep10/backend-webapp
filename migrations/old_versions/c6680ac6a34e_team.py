"""team

Revision ID: c6680ac6a34e
Revises: d6d14b05e3d8
Create Date: 2025-06-29 16:27:21.592218

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c6680ac6a34e'
down_revision: Union[str, Sequence[str], None] = 'd6d14b05e3d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_teams",
        *common_columns(),
        sa.Column('name',sa.String(250),nullable=False),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("sys_organizations.id"), nullable=False, index=True),
        sa.Column('description',sa.String(250),nullable=False)
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('org_teams')