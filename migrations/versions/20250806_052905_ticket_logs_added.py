"""Ticket Logs added

Revision ID: 20250806_052905
Revises: 20250803_053316
Create Date: 2025-08-06 11:14:06.024090

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250806_052905"
down_revision: Union[str, Sequence[str], None] = "20250803_053316"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketLogMigration(BaseMigration):

    table_name = "org_tickets_logs"

    def __init__(self):
        super().__init__(revision="20250806_052905", down_revision="20250803_053316")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.foreign(
            name="ticket_id", table="org_tickets", ondelete="SET NULL", nullable=True
        )
        self.string(name="entity_type", nullable=False)
        self.string(name="action", nullable=False)
        self.string(name="description", nullable=True)
        self.json(name="previous_value", nullable=True)
        self.json(name="new_value", nullable=True)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketLogMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketLogMigration().downgrade()
