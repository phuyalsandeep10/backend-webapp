"""organization member roles

Revision ID: ecea4cbf8ed8
Revises: 14b296459f7c
Create Date: 2025-06-27 11:43:17.240934

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns 


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecea4cbf8ed8'
down_revision: Union[str, Sequence[str], None] = '14b296459f7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sys_organization_member_roles",
        *common_columns(),
        sa.Column("member_id", sa.Integer, sa.ForeignKey("sys_organization_members.id"), nullable=False, index=True),  
        sa.Column("role_id",sa.Integer, sa.ForeignKey("sys_organization_roles.id"),nullable=False, index=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sys_organization_member_roles")
