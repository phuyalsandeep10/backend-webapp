"""ticket email log table added

Revision ID: 03f996d78561
Revises: ea8c22fe9b79
Create Date: 2025-07-24 16:24:11.382957

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migrations.common import base_columns

# revision identifiers, used by Alembic.
revision: str = "03f996d78561"
down_revision: Union[str, Sequence[str], None] = "0153f2ba2a04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "ticket_email_log",
        *base_columns(),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column(
            "email_type",
            sa.String(),
            nullable=False,
        ),
        sa.Column("recipient", sa.String(), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["org_tickets.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ticket_email_log")
