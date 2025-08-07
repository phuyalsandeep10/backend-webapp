"""ticket alert table added

Revision ID: 20250803_053126
Revises: 20250803_052710
Create Date: 2025-08-03 11:16:26.524621

"""

from datetime import datetime
from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250803_053126"
down_revision: Union[str, Sequence[str], None] = "20250803_052710"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketAlertMigration(BaseMigration):

    table_name = "ticket_alerts"

    def __init__(self):
        super().__init__(revision="20250803_053126", down_revision="20250803_052710")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.foreign(name="ticket_id", table="org_tickets", ondelete="CASCADE")
        self.string(name="alert_type")
        self.string(name="warning_level")
        self.date_time(name="sent_at", default=datetime.utcnow)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketAlertMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketAlertMigration().downgrade()
