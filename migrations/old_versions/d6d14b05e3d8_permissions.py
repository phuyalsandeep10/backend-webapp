"""permissions

Revision ID: d6d14b05e3d8
Revises: ecea4cbf8ed8
Create Date: 2025-06-27 12:46:56.675415

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd6d14b05e3d8'
down_revision: Union[str, Sequence[str], None] = 'ecea4cbf8ed8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "sys_permissions",
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name',sa.String(250),nullable=False,unique=True),
        sa.Column('identifier',sa.String(250), nullable=False,unique=True),
        sa.Column('description',sa.String(250), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "sys_permissions"
    )
