"""priority table added

Revision ID: 0d37df01ec47
Revises: dccc09a8929f
Create Date: 2025-07-24 16:23:05.987000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.common import common_columns

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
        sa.Column("bg_color", sa.String(), nullable=False),
        sa.Column("fg_color", sa.String(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["sys_organizations.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "organization_id", "name", "level", name="uniq_org_name_level"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    ticket_priority_table = sa.table(
        "ticket_priority",
        *common_columns(),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("bg_color", sa.String(), nullable=False),
        sa.Column("fg_color", sa.String(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )

    op.bulk_insert(
        ticket_priority_table,
        [
            {
                "id": 1,
                "name": "critical",
                "level": "0",
                "bg_color": "#FAD6D5",
                "fg_color": "#F61818",
                "organization_id": None,
            },
            {
                "id": 2,
                "name": "high",
                "level": "1",
                "bg_color": "#FFF0D2",
                "fg_color": "#F5CE31",
                "organization_id": None,
            },
            {
                "id": 3,
                "name": "medium",
                "level": "2",
                "bg_color": "#DAE8FA",
                "fg_color": "#3872B7",
                "organization_id": None,
            },
            {
                "id": 4,
                "name": "low",
                "level": "3",
                "bg_color": "#E5F9DB",
                "fg_color": "#009959",
                "organization_id": None,
            },
        ],
    )

    # to manage id_seq

    op.execute(
        "SELECT setval('ticket_priority_id_seq', (SELECT MAX(id) FROM ticket_priority))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ticket_priority")
