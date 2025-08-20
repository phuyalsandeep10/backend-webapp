"""ticket table added

Revision ID: 20250803_051947
Revises: 20250803_051346
Create Date: 2025-08-03 11:04:47.849951

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250803_051947"
down_revision: Union[str, Sequence[str], None] = "20250803_051346"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketMigration(BaseMigration):
    table_name = "org_tickets"

    def __init__(self):
        super().__init__(revision="20250803_051947", down_revision="20250803_051346")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.string(name="title")
        self.string(name="description")
        self.string(name="attachment", nullable=True)
        self.string(name="sender_domain", nullable=False)
        self.string(name="notes", nullable=True)
        self.foreign(name="priority_id", table="ticket_priority", ondelete="SET NULL")
        self.foreign(name="status_id", table="ticket_status", ondelete="SET NULL")
        self.foreign(name="department_id", table="org_teams", ondelete="SET NULL")
        self.foreign(name="sla_id", table="ticket_sla", ondelete="SET NULL")
        self.foreign(
            name="customer_id",
            table="org_customers",
            ondelete="SET NULL",
            nullable=True,
        )
        self.boolean(name="is_spam", default=False)
        self.string(name="customer_name", nullable=True)
        self.string(name="customer_email", nullable=True)
        self.string(name="customer_phone", nullable=True)
        self.string(name="customer_location", nullable=True)
        self.string(name="confirmation_token", nullable=True)
        self.date_time(name="opened_at", nullable=True)
        self.date_time(name="resolved_at", nullable=True)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketMigration().downgrade()
