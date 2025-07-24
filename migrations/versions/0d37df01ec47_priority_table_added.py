"""priority table added

Revision ID: 0d37df01ec47
Revises: dccc09a8929f
Create Date: 2025-07-24 16:23:05.987000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d37df01ec47"
down_revision: Union[str, Sequence[str], None] = "569993d68ff6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
