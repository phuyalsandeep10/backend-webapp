"""Add RolePermission table

Revision ID: 20250804_062017
Revises: 20250804_055307
Create Date: 2025-08-04 12:05:18.303497

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250804_062017"
down_revision: Union[str, Sequence[str], None] = "20250804_055307"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class RolePermissionMigration(BaseMigration):

    table_name = "role_permissions"

    def __init__(self):
        super().__init__(revision="20250804_062017", down_revision="20250804_055307")
        self.create_whole_table = True
        self.common_columns()

        self.foreign("permission_id", "permissions")

        self.foreign("role_id", "org_roles")

        self.boolean("is_changeable", default=False, nullable=True)
        self.boolean("is_deletable", default=False, nullable=True)
        self.boolean("is_viewable", default=False, nullable=True)
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    RolePermissionMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    RolePermissionMigration().downgrade()
