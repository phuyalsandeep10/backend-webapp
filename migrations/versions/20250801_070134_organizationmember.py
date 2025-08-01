"""organizationmember

Revision ID: 20250801_070134
Revises: 20250801_020657
Create Date: 2025-08-01 12:46:35.656860

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_070134"
down_revision: Union[str, Sequence[str], None] = "20250801_020657"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrganizationmemberMigration(BaseMigration):

    table_name = "org_members"

    def __init__(self):
        super().__init__(revision="20250801_070134", down_revision="20250801_020657")

        self.common_columns()
        self.foreign("user_id", "sys_users")
        self.foreign("organization_id", "sys_organizations")

        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    OrganizationmemberMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrganizationmemberMigration().downgrade()
