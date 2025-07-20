"""ticket alert added

Revision ID: c339bd54d370
Revises: 422ff03cf2c7
Create Date: 2025-07-20 10:04:49.750888

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c339bd54d370"
down_revision: Union[str, Sequence[str], None] = "422ff03cf2c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ticket_alerts",
        sa.Column(
            "ticket_id",
            sa.Integer,
            sa.ForeignKey("tickets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "alert_type",
            sa.Enum("RESOLUTION", "RESPONSE", name="ticketalerttypeenum"),
            nullable=False,
        ),
        sa.Column(
            "warning_level",
            sa.Enum("WARNING_75", "WARNING_90", "WARNING_100", name="warninglevelenum"),
            nullable=False,
        ),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ticket_alerts")
