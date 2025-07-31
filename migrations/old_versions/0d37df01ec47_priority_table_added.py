"""priority table added

Revision ID: 0d37df01ec47
Revises: dccc09a8929f
Create Date: 2025-07-24 16:23:05.987000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

from migrations.common import base_columns, common_columns

# revision identifiers, used by Alembic.
revision: str = "0d37df01ec47"
down_revision: Union[str, Sequence[str], None] = "569993d68ff6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ticket_priority",
        *common_columns(),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["sys_organizations.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("organization_id", "name", name="uniq_org_name"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ticket_priority")
