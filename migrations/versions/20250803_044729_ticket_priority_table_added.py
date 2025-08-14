"""ticket priority table added

Revision ID: 20250803_044729
Revises: 20250801_091606
Create Date: 2025-08-03 10:32:30.150870

"""

from typing import Sequence, Union

from alembic import op
from sqlmodel import func

from migrations.base import BaseMigration
from src.modules.ticket.models.priority import TicketPriority

revision: str = "20250803_044729"
down_revision: Union[str, Sequence[str], None] = "20250801_091606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketPriorityMigration(BaseMigration):

    table_name = "ticket_priority"

    def __init__(self):
        super().__init__(revision="20250803_044729", down_revision="20250801_091606")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.string(name="name")
        self.integer(name="level")
        self.string(name="bg_color")
        self.string(name="fg_color")
        self.unique_constraint(
            "organization_id",
            "name",
            "level",
        )
        self.unique_constraint(
            "organization_id",
            "level",
        )
        self.unique_constraint("organization_id", "name")


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketPriorityMigration().upgrade()
    # default_priorities = [
    #     {
    #         "id": 1,
    #         "name": "critical",
    #         "level": "0",
    #         "bg_color": "#FAD6D5",
    #         "fg_color": "#F61818",
    #         "organization_id": None,
    #     },
    #     {
    #         "id": 2,
    #         "name": "high",
    #         "level": "1",
    #         "bg_color": "#FFF0D2",
    #         "fg_color": "#F5CE31",
    #         "organization_id": None,
    #     },
    #     {
    #         "id": 3,
    #         "name": "medium",
    #         "level": "2",
    #         "bg_color": "#DAE8FA",
    #         "fg_color": "#3872B7",
    #         "organization_id": None,
    #     },
    #     {
    #         "id": 4,
    #         "name": "low",
    #         "level": "3",
    #         "bg_color": "#E5F9DB",
    #         "fg_color": "#009959",
    #         "organization_id": None,
    #     },
    # ]
    # TicketPriorityMigration().bulk_insert_data(rows=default_priorities)
    # op.execute(
    #     "SELECT setval('ticket_priority_id_seq', (SELECT MAX(id) FROM ticket_priority))"
    # )


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketPriorityMigration().downgrade()
