"""Add PermissionGroup table

Revision ID: 20250804_055139
Revises: 20250801_091606
Create Date: 2025-08-04 11:36:40.263350

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250804_055139"
down_revision: Union[str, Sequence[str], None] = "20250801_091606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class PermissionGroupMigration(BaseMigration):

    table_name = "sys_permissions_groups"

    def __init__(self):
        super().__init__(revision="20250804_055139", down_revision="20250801_091606")
        self.create_whole_table = True
        self.base_columns()
        self.string("name")
        
        
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    PermissionGroupMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    PermissionGroupMigration().downgrade()
