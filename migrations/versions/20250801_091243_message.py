"""message

Revision ID: 20250801_091243
Revises: 20250801_090823
Create Date: 2025-08-01 14:57:43.840256

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_091243"
down_revision: Union[str, Sequence[str], None] = "20250801_090823"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class MessageMigration(BaseMigration):

    table_name = ""

    def __init__(self):
        super().__init__(revision="20250801_091243", down_revision="20250801_090823")
        self.common_columns()
        self.foreign("conversation_id", "org_conversations")
        self.foreign("user_id", "sys_users")
        self.string("content", nullable=False)
        self.foreign("customer_id", "org_customers")
        self.string("feedback", nullable=True)
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    MessageMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    MessageMigration().downgrade()
