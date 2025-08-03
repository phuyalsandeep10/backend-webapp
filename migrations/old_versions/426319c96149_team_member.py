"""team member

Revision ID: 426319c96149
Revises: c6680ac6a34e
Create Date: 2025-06-30 10:05:39.548591

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '426319c96149'
down_revision: Union[str, Sequence[str], None] = 'c6680ac6a34e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_team_members",
        *common_columns(),
    
        sa.Column("user_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=False, index=True),
        sa.Column("team_id", sa.Integer, sa.ForeignKey("org_teams.id"), nullable=False, index=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "org_team_members"
    )
