"""ticket email log table added

Revision ID: 03f996d78561
Revises: ea8c22fe9b79
Create Date: 2025-07-24 16:24:11.382957

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03f996d78561'
down_revision: Union[str, Sequence[str], None] = 'ea8c22fe9b79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
