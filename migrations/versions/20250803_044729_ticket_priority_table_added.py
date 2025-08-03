"""ticket priority table added

Revision ID: 20250803_044729
Revises: 20250801_091606
Create Date: 2025-08-03 10:32:30.150870

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

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


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketPriorityMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketPriorityMigration().downgrade()
