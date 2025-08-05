"""ticket email log addded

Revision ID: 20250803_053316
Revises: 20250803_053126
Create Date: 2025-08-03 11:18:16.474833

"""

from datetime import datetime
from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250803_053316"
down_revision: Union[str, Sequence[str], None] = "20250803_053126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketEmailLogMigration(BaseMigration):

    table_name = "ticket_email_log"

    def __init__(self):
        super().__init__(revision="20250803_053316", down_revision="20250803_053126")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.foreign(name="ticket_id", table="org_tickets", ondelete="CASCADE")
        self.string(name="email_type")
        self.string(name="recipient")
        self.date_time(name="sent_at", default=datetime.utcnow)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketEmailLogMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketEmailLogMigration().downgrade()
