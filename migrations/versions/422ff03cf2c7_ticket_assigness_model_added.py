"""ticket assigness model added

Revision ID: 422ff03cf2c7
Revises: 6aeb44fec6af
Create Date: 2025-07-17 14:35:14.480653

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "422ff03cf2c7"
down_revision: Union[str, Sequence[str], None] = "03f996d78561"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "ticket_assignees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "ticket_id",
            sa.Integer,
            sa.ForeignKey("org_tickets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assignee_id",
            sa.Integer,
            sa.ForeignKey("sys_users.id", ondelete="SET NULL"),
        ),
    )


def downgrade():
    op.drop_table("ticket_assignees")
