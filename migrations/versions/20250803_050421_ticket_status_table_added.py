"""ticket status table added

Revision ID: 20250803_050421
Revises: 20250803_044729
Create Date: 2025-08-03 10:49:21.461892

"""

from typing import Sequence, Union

from alembic import op

from migrations.base import BaseMigration

revision: str = "20250803_050421"
down_revision: Union[str, Sequence[str], None] = "20250803_044729"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketStatusMigration(BaseMigration):

    table_name = "ticket_status"

    def __init__(self):
        super().__init__(revision="20250803_050421", down_revision="20250803_044729")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.string(name="name")
        self.string(name="bg_color")
        self.string(name="fg_color")
        self.boolean(name="is_default", default=False)
        self.string(name="status_category")
        self.unique_constraint(
            "organization_id",
            "name",
        )


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketStatusMigration().upgrade()
    default_ticket_status = [
        {
            "id": 1,
            "name": "Unassigned",
            "bg_color": "#F61818",
            "fg_color": "#ffffff",
            "organization_id": None,
            "status_category": "pending",
            "is_default": True,
        },
        {
            "id": 2,
            "name": "Assigned",
            "bg_color": "#FFF0D2",
            "fg_color": "#ffffff",
            "organization_id": None,
            "status_category": "open",
            "is_default": False,
        },
        {
            "id": 3,
            "name": "Solved",
            "bg_color": "#009959",
            "fg_color": "#ffffff",
            "organization_id": None,
            "status_category": "closed",
            "is_default": False,
        },
        {
            "id": 4,
            "name": "Reopened",
            "bg_color": "#DAE8FA",
            "fg_color": "#ffffff",
            "organization_id": None,
            "status_category": "open",
            "is_default": False,
        },
    ]
    TicketStatusMigration().bulk_insert_data(rows=default_ticket_status)

    op.execute(
        "SELECT setval('ticket_status_id_seq', (SELECT MAX(id) FROM ticket_status))"
    )


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketStatusMigration().downgrade()
