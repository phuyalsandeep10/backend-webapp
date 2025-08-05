"""organization

Revision ID: 20250801_020657
Revises: 20250801_020510
Create Date: 2025-08-01 07:51:57.544097

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_020657"
down_revision: Union[str, Sequence[str], None] = "20250801_020510"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrganizationMigration(BaseMigration):

    table_name = "sys_organizations"

    def __init__(self):
        super().__init__(revision="20250801_020657", down_revision="20250801_020510")
        # describe your schemas here
        self.common_columns()
        self.string("name", nullable=False, unique=True, index=True)
        self.string("description", nullable=True, default=None)
        self.string("slug", nullable=False, unique=True, index=True)
        self.string("logo", nullable=True, default=None)
        self.string("domain", nullable=False, index=True)
        self.string("contact_email", nullable=True, default=None)
        self.string("contact_dial_code")
        self.string("contact_phone", nullable=True, default=None)
        self.string("address")
        self.string("purpose")
        self.string("identifier", unique=True, nullable=False, index=True)
        self.string("time_zone")
        self.foreign("owner_id", "sys_users")
        self.string("telegram_username")
        self.string("facebook_username")
        self.string("whatsapp_number")
        self.string("twitter_username")


def upgrade() -> None:
    """
    Function to create a table
    """

    OrganizationMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrganizationMigration().downgrade()
