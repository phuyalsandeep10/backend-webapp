"""ticket sla table added

Revision ID: 20250803_051346
Revises: 20250803_050421
Create Date: 2025-08-03 10:58:47.312924

"""

from typing import Sequence, Union

from alembic import op

from migrations.base import BaseMigration

revision: str = "20250803_051346"
down_revision: Union[str, Sequence[str], None] = "20250803_050421"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketSLAMigration(BaseMigration):

    table_name = "ticket_sla"

    def __init__(self):
        super().__init__(revision="20250803_051346", down_revision="20250803_050421")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.string(name="name")
        self.biginteger(name="response_time")
        self.boolean(name="is_default", default=False)
        self.biginteger(name="resolution_time")
        self.foreign(name="priority_id", table="ticket_priority")
        self.unique_constraint("organization_id", "name", "priority_id")


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketSLAMigration().upgrade()
    default_ticket_sla = [
        {
            "id": 1,
            "name": "Critical Standard",
            "response_time": "14400",  # 4 hours in seconds
            "resolution_time": "86400",  # 24 hours in seconds
            "organization_id": None,
            "priority_id": 1,
            "is_default": False

        },
        {
            "id": 2,
            "name": "High Standard",
            "response_time": "18400",
            "resolution_time": "106400",
            "organization_id": None,
            "priority_id": 2,
        },
        {
            "id": 3,
            "name": "Medium Standard",
            "response_time": "22400",
            "resolution_time": "146400",
            "organization_id": None,
            "priority_id": 3,
        },
        {
            "id": 4,
            "name": "Low Standard",
            "response_time": "30400",
            "resolution_time": "206400",
            "organization_id": None,
            "priority_id": 2,
        },
    ]
    TicketSLAMigration().bulk_insert_data(rows=default_ticket_sla)
    op.execute("SELECT setval('ticket_sla_id_seq', (SELECT MAX(id) FROM ticket_sla))")


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketSLAMigration().downgrade()
