"""Add Permission_group table

Revision ID: 20250803_104545
Revises: 20250801_091606
Create Date: 2025-08-03 16:30:45.444342

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250803_104545"
down_revision: Union[str, Sequence[str], None] = "20250801_091606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class Permission_groupMigration(BaseMigration):

    table_name = "permission_groups"

    def __init__(self):
        super().__init__(revision="20250803_104545", down_revision="20250801_091606")
        self.create_whole_table = True
        self.common_columns()
        self.string("name")


def upgrade() -> None:
    """
    Function to create a table
    """
    Permission_groupMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    Permission_groupMigration().downgrade()
