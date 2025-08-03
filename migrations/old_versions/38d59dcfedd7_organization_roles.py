"""organization roles

Revision ID: 38d59dcfedd7
Revises: 610a4d0690ad
Create Date: 2025-06-25 11:16:59.546320

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa
from migrations.common import common_columns


# revision identifiers, used by Alembic.
revision: str = '38d59dcfedd7'
down_revision: Union[str, Sequence[str], None] = '610a4d0690ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("sys_organization_roles",
    *common_columns(), 
    sa.Column("organization_id", sa.Integer, sa.ForeignKey("sys_organizations.id"), nullable=False, index=True),
    sa.Column('name',sa.String(255), nullable=False),
    sa.Column('description',sa.String(500),nullable=True),
    sa.Column('identifier',sa.String(255),nullable=False),
    sa.Column(
            'permissions', sa.JSON, nullable=True, default=[]
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('sys_organization_roles')
