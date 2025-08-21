"""refreshtoken

Revision ID: 20250801_015459
Revises: 20250731_023113
Create Date: 2025-08-01 07:39:59.996367

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_015459"
down_revision: Union[str, Sequence[str], None] = "20250731_023113"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class RefreshTokenMigration(BaseMigration):
    table_name = "refresh_tokens"

    def __init__(self):
        super().__init__(revision="20250801_015459", down_revision="20250731_023113")
        self.common_columns()
        self.foreign("user_id", "sys_users", ondelete="CASCADE")
        self.string("token", nullable=False)
        self.date_time("expires_at", nullable=False)
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    RefreshTokenMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    RefreshTokenMigration().downgrade()
