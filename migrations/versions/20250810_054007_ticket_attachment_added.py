"""ticket attachment added

Revision ID: 20250810_054007
Revises: 20250806_052905
Create Date: 2025-08-10 11:25:08.374141

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250810_054007"
down_revision: Union[str, Sequence[str], None] = "20250806_052905"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TicketAttachmentMigration(BaseMigration):
    table_name = "ticket_attachments"

    def __init__(self):
        super().__init__(revision="20250810_054007", down_revision="20250806_052905")
        self.create_whole_table = True
        # describe your schemas here
        self.common_columns()
        self.foreign(name="ticket_id", table="org_tickets", ondelete="CASCADE")
        self.string(name="attachment")


def upgrade() -> None:
    """
    Function to create a table
    """
    TicketAttachmentMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TicketAttachmentMigration().downgrade()
