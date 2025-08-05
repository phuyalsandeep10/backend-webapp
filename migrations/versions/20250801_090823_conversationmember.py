"""conversationmember

Revision ID: 20250801_090823
Revises: 20250801_090511
Create Date: 2025-08-01 14:53:24.525373

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_090823"
down_revision: Union[str, Sequence[str], None] = "20250801_090511"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class ConversationmemberMigration(BaseMigration):

    table_name = "org_conversation_members"

    def __init__(self):
        super().__init__(revision="20250801_090823", down_revision="20250801_090511")
        self.common_columns()
        self.foreign("conversation_id", "org_conversations")
        self.foreign("user_id", "sys_users")

        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    ConversationmemberMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    ConversationmemberMigration().downgrade()
