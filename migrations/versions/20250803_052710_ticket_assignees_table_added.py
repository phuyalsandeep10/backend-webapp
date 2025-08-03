"""ticket assignees table added

Revision ID: 20250803_052710
Revises: 20250803_051947
Create Date: 2025-08-03 11:12:10.801179

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250803_052710"
down_revision: Union[str, Sequence[str], None] = "20250803_051947"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketAssigneeMigration(BaseMigration):

    table_name = "ticket_assignees"

    def __init__(self):
        super().__init__(revision="20250803_052710", down_revision="20250803_051947")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.foreign(name="ticket_id", table="org_tickets", ondelete="CASCADE")
        self.foreign(name="assignee_id", table="sys_users", ondelete="CASCADE")


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketAssigneeMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketAssigneeMigration().downgrade()
