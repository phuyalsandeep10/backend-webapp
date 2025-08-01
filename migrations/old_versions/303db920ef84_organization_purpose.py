"""organization purpose

Revision ID: 303db920ef84
Revises: dccc09a8929f
Create Date: 2025-07-23 16:11:35.107615

"""

from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "303db920ef84"
down_revision: Union[str, Sequence[str], None] = "dccc09a8929f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sys_organizations", sa.Column("purpose", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sys_organizations", "purpose")
