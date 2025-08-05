"""teammember

Revision ID: 20250801_085215
Revises: 20250801_084656
Create Date: 2025-08-01 14:37:15.988909

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_085215"
down_revision: Union[str, Sequence[str], None] = "20250801_084656"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TeammemberMigration(BaseMigration):

    table_name = "org_team_members"

    def __init__(self):
        super().__init__(revision="20250801_085215", down_revision="20250801_084656")
        self.common_columns()
        self.foreign("team_id", "org_teams")
        self.foreign("user_id", "sys_users")
        self.string("role")
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    TeammemberMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TeammemberMigration().downgrade()
