"""invitation

Revision ID: 14b296459f7c
Revises: 38d59dcfedd7
Create Date: 2025-06-26 14:24:43.833592

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14b296459f7c'
down_revision: Union[str, Sequence[str], None] = '38d59dcfedd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sys_organization_invitations",
        *common_columns(),
        sa.Column(
            "email",
            sa.String(250),
        ),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("sys_organizations.id"), nullable=False),
        sa.Column("status",sa.String(100)),
        sa.Column("invited_by_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=False, index=True),
        sa.Column('role_ids',sa.JSON,nullable=False)
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sys_organization_invitations")
