"""invitation_role table

Revision ID: 20250814_095326
Revises: 20250804_062017
Create Date: 2025-08-14 15:38:26.693032

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250814_095326"
down_revision: Union[str, Sequence[str], None] = "20250804_062017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class invitation_rolesMigration(BaseMigration):

    table_name = "org_invitation_roles"

    def __init__(self):
        super().__init__(revision="20250814_095326", down_revision="20250804_062017")
        self.create_whole_table = True
        self.common_columns()
        self.foreign("invitation_id", "org_invitations")
        self.foreign("role_id", "org_roles")

        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    invitation_rolesMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    invitation_rolesMigration().downgrade()
