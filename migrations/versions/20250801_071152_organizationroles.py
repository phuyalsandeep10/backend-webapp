"""organizationroles

Revision ID: 20250801_071152
Revises: 20250801_070134
Create Date: 2025-08-01 12:56:52.882907

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_071152"
down_revision: Union[str, Sequence[str], None] = "20250801_070134"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrganizationrolesMigration(BaseMigration):

    table_name = "org_roles"

    def __init__(self):
        super().__init__(revision="20250801_071152", down_revision="20250801_070134")
        self.tenant_columns()
        self.string("name")
        self.string("description")
        self.string("identifier")
        self.json("attributes", default={})
        # self.json("permissions", default=[])
        # self.foreign("organization_id", "sys_organizations")

        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    OrganizationrolesMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrganizationrolesMigration().downgrade()
