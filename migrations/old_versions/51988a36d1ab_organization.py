"""organization

Revision ID: 51988a36d1ab
Revises: 6bbd80a33f72
Create Date: 2025-06-25 10:45:58.501358

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns 


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51988a36d1ab'
down_revision: Union[str, Sequence[str], None] = '6bbd80a33f72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("sys_organizations",
        *common_columns(),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("description", sa.String(500), nullable=True, default=None),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("logo", sa.String(255), nullable=True, default=None),
        sa.Column("website", sa.String(255), nullable=True, default=None),
    ) 
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sys_organizations")
