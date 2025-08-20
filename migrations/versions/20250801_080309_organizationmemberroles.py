"""organizationmemberroles

Revision ID: 20250801_080309
Revises: 20250801_071152
Create Date: 2025-08-01 13:48:10.748815

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_080309"
down_revision: Union[str, Sequence[str], None] = "20250801_071152"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrganizationMemberRolesMigration(BaseMigration):
    table_name = "org_member_roles"

    def __init__(self):
        super().__init__(revision="20250801_080309", down_revision="20250801_071152")
        # describe your schemas here
        self.common_columns()
        self.foreign("organization_id", "sys_organizations")
        self.foreign("role_id", "org_roles")
        self.foreign("member_id", "org_members")


def upgrade() -> None:
    """
    Function to create a table
    """
    OrganizationMemberRolesMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrganizationMemberRolesMigration().downgrade()
