"""your message

Revision ID: 803c433dc2f4
Revises: 
Create Date: 2025-06-23 12:56:31.165996
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from migrations.common import timestamp_columns


# revision identifiers, used by Alembic.
revision: str = '803c433dc2f4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sys_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=True),
        sa.Column('image', sa.String, nullable=True),
        sa.Column('mobile', sa.String, unique=True, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean, default=False, nullable=False),
        sa.Column('is_staff', sa.Boolean, default=False, nullable=False),
        sa.Column('email_verified_at', sa.DateTime, default=False, nullable=True),
        sa.Column(
            'attributes', sa.JSON, nullable=True, default=None
        ),
        *timestamp_columns()
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('sys_users')

    # ### end Alembic commands ###
