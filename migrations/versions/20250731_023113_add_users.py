"""add users

Revision ID: 20250731_023113
Revises:
Create Date: 2025-07-31 08:16:13.360813

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250731_023113"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class add_users_tableMigration(BaseMigration):
    table_name = "sys_users"

    def __init__(self):
        super().__init__(revision="20250731_023113", down_revision=None)
        # describe your schemas here
        self.primary_key()
        self.string("name")
        self.string("email", unique=True, index=True)
        self.string("mobile", unique=True, index=True)
        self.string("image", nullable=True)
        self.string("address", nullable=True)
        self.string("country", nullable=True)
        self.string("language", nullable=True, default="English")
        self.string("password", nullable=True)
        self.date_time("email_verified_at", nullable=True)
        self.date_time("mobile_verified_at", nullable=True)
        self.boolean("is_active", default=True)

        self.boolean("is_superuser", default=False)
        self.boolean("is_staff", default=False)
        self.json("attributes", nullable=True, default={})

        self.boolean("two_fa_enabled", default=False)
        self.string("two_fa_secret")
        self.string("two_fa_auth_url", nullable=True)

        self.timestamp_columns()
        self.date_time("deleted_at")


def upgrade() -> None:
    """
    Function to create a table
    """

    add_users_tableMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """

    add_users_tableMigration().downgrade()
