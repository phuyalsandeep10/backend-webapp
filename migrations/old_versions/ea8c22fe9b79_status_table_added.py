"""status table added

Revision ID: ea8c22fe9b79
Revises: 0d37df01ec47
Create Date: 2025-07-24 16:23:56.515786

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

from migrations.common import base_columns, common_columns

# revision identifiers, used by Alembic.
revision: str = "ea8c22fe9b79"
down_revision: Union[str, Sequence[str], None] = "0d37df01ec47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ticket_status",
        *common_columns(),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("bg_color", sa.String(), nullable=False),
        sa.Column("fg_color", sa.String(), nullable=False),
        sa.Column("is_default", sa.Boolean(), default=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("status_category", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["sys_organizations.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("organization_id", "name", name="uniq_org_status_name"),
    )

    ticket_status_table = sa.table(
        "ticket_status",
        *common_columns(),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("bg_color", sa.String(), nullable=False),
        sa.Column("fg_color", sa.String(), nullable=False),
        sa.Column("is_default", sa.Boolean(), default=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("status_category", sa.String(), nullable=False),
    )
    op.bulk_insert(
        ticket_status_table,
        [
            {
                "id": 1,
                "name": "Unassigned",
                "bg_color": "#F61818",
                "fg_color": "#ffffff",
                "organization_id": None,
                "status_category": "pending",
            },
            {
                "id": 2,
                "name": "Assigned",
                "bg_color": "#FFF0D2",
                "fg_color": "#ffffff",
                "organization_id": None,
                "status_category": "open",
            },
            {
                "id": 3,
                "name": "Solved",
                "bg_color": "#009959",
                "fg_color": "#ffffff",
                "organization_id": None,
                "status_category": "closed",
            },
            {
                "id": 4,
                "name": "Reopened",
                "bg_color": "#DAE8FA",
                "fg_color": "#ffffff",
                "organization_id": None,
                "status_category": "open",
            },
        ],
    )

    op.execute(
        "SELECT setval('ticket_status_id_seq', (SELECT MAX(id) FROM ticket_status))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.op.drop_table("ticket_status")
