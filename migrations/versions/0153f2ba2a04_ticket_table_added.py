"""ticket table added

Revision ID: 0153f2ba2a04
Revises: 569993d68ff6
Create Date: 2025-07-20 09:21:27.745427

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.common import common_columns

# revision identifiers, used by Alembic.
revision: str = "0153f2ba2a04"
down_revision: Union[str, Sequence[str], None] = "ea8c22fe9b79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "org_tickets",
        *common_columns(),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("attachment", sa.String(length=255), nullable=True),
        sa.Column("sender_domain", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("confirmation_token", sa.String(), nullable=True),
        sa.Column("opened_at", sa.DateTime, nullable=True),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("sys_organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "priority_id",
            sa.Integer,
            sa.ForeignKey("ticket_priority.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "status_id",
            sa.Integer,
            sa.ForeignKey("ticket_status.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "department_id",
            sa.Integer,
            sa.ForeignKey("org_teams.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "sla_id",
            sa.Integer,
            sa.ForeignKey("ticket_sla.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "customer_id",
            sa.Integer,
            sa.ForeignKey("org_customers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_spam", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("customer_phone", sa.String(length=50), nullable=True),
        sa.Column("customer_location", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_tickets")
