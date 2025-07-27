"""sla table added

Revision ID: 569993d68ff6
Revises: d83e3f5df43d
Create Date: 2025-07-20 09:12:50.753983

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

from migrations.common import common_columns

# revision identifiers, used by Alembic.
revision: str = "569993d68ff6"
down_revision: Union[str, Sequence[str], None] = "d83e3f5df43d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ticket_sla",
        *common_columns(),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_time", sa.BigInteger(), nullable=False),
        sa.Column("resolution_time", sa.BigInteger(), nullable=False),
        sa.Column("issued_by", sa.Integer(), nullable=False),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("sys_organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ticket_sla")
