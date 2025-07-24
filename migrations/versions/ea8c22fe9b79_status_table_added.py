"""status table added

Revision ID: ea8c22fe9b79
Revises: 0d37df01ec47
Create Date: 2025-07-24 16:23:56.515786

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea8c22fe9b79'
down_revision: Union[str, Sequence[str], None] = '0d37df01ec47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
