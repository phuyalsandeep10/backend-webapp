"""organization member

Revision ID: 610a4d0690ad
Revises: 51988a36d1ab
Create Date: 2025-06-25 11:03:50.977953

"""

from typing import Sequence, Union
import sqlmodel.sql.sqltypes
from migrations.common import common_columns

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "610a4d0690ad"
down_revision: Union[str, Sequence[str], None] = "51988a36d1ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sys_organization_members",
        *common_columns(),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("sys_organizations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("user_id", sa.Integer, nullable=False, index=True),
        sa.Column("is_owner", sa.Boolean, default=False, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sys_organization_members")
