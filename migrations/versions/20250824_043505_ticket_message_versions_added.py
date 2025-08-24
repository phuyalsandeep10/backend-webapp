"""Ticket message versions added

Revision ID: 20250824_043505
Revises: 20250819_051645
Create Date: 2025-08-24 10:20:06.443396

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250824_043505"
down_revision: Union[str, Sequence[str], None] = "20250819_072251"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketMessageVersionMigration(BaseMigration):

    table_name = "ticket_messages_versions"

    def __init__(self):
        super().__init__(revision="20250824_043505", down_revision="20250819_051645")
        self.create_whole_table = True
        # describe your schemas here
        self.tenant_columns()
        self.foreign(name="message_id", table="ticket_messages", ondelete="CASCADE")
        self.integer(name="versions", nullable=False)
        self.string(name="content", nullable=False)


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketMessageVersionMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketMessageVersionMigration().downgrade()
