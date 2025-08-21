"""organizationinvitation

Revision ID: 20250801_083808
Revises: 20250801_080309
Create Date: 2025-08-01 14:23:08.710458

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_083808"
down_revision: Union[str, Sequence[str], None] = "20250801_080309"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrganizationinvitationMigration(BaseMigration):
    table_name = "org_invitations"

    def __init__(self):
        super().__init__(revision="20250801_083808", down_revision="20250801_080309")
        self.tenant_columns()
        self.string("email", nullable=False)
        self.string("name", nullable=False)
        self.string("status", nullable=False)
        self.foreign("invited_by_id", "sys_users", ondelete="CASCADE")
        self.date_time("expires_at", nullable=False)
        self.date_time("activity_at", nullable=True)
        self.json("role_ids", nullable=False, default=[])
        self.string("token", nullable=False)


def upgrade() -> None:
    """
    Function to create a table
    """
    OrganizationinvitationMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrganizationinvitationMigration().downgrade()
