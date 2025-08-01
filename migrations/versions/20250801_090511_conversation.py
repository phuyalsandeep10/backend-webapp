"""conversation

Revision ID: 20250801_090511
Revises: 20250801_085926
Create Date: 2025-08-01 14:50:12.662205

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_090511"
down_revision: Union[str, Sequence[str], None] = "20250801_085926"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class ConversationMigration(BaseMigration):

    table_name = "org_conversations"

    def __init__(self):
        super().__init__(revision="20250801_090511", down_revision="20250801_085926")
        self.common_columns()
        self.foreign("organization_id", "sys_organizations")
        self.foreign("customer_id", "org_customers")
        self.string("name", nullable=True)
        self.foreign("assigned_user_id", "sys_users")


def upgrade() -> None:
    """
    Function to create a table
    """
    ConversationMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    ConversationMigration().downgrade()
