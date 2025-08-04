"""Add Permission table

Revision ID: 20250804_055307
Revises: 20250804_055139
Create Date: 2025-08-04 11:38:08.248833

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250804_055307"
down_revision: Union[str, Sequence[str], None] = "20250804_055139"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class PermissionMigration(BaseMigration):

    table_name = "permissions"

    def __init__(self):
        super().__init__(revision="20250804_055307", down_revision="20250804_055139")
        self.create_whole_table = True
        self.base_columns()
        self.string("name")

        self.foreign(
            "group_id",
            "sys_permissions_groups",
        )
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    PermissionMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    PermissionMigration().downgrade()
