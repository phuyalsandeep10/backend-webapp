"""ticket_message_table_added

Revision ID: 20250819_051645
Revises: 20250814_033142
Create Date: 2025-08-19 11:01:45.801131

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250819_051645"
down_revision: Union[str, Sequence[str], None] = "20250814_033142"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketMessageMigration(BaseMigration):

    table_name = "ticket_messages"

    def __init__(self):
        super().__init__(revision="20250819_051645", down_revision="20250814_033142")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.foreign(
            name="ticket_id", table="org_tickets", ondelete="CASCADE", nullable=False
        )
        self.string(name="sender", nullable=False)
        self.string(name="receiver", nullable=False)
        self.string(name="direction")
        self.string(name="content")
        self.string(name="attachments", nullable=True)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketMessageMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketMessageMigration().downgrade()
