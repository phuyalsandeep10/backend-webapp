"""messageattachements

Revision ID: 20250801_091606
Revises: 20250801_091243
Create Date: 2025-08-01 15:01:07.069500

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_091606"
down_revision: Union[str, Sequence[str], None] = "20250801_091243"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class MessageattachementsMigration(BaseMigration):

    table_name = "org_message_attachments"

    def __init__(self):
        super().__init__(revision="20250801_091606", down_revision="20250801_091243")
        self.common_columns()
        self.foreign("message_id", "org_messages")
        self.string("file_name", nullable=False)
        self.string("file_type", nullable=False)
        self.string("file_size", nullable=False)
        self.string("file_url", nullable=False)


def upgrade() -> None:
    """
    Function to create a table
    """
    MessageattachementsMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    MessageattachementsMigration().downgrade()
