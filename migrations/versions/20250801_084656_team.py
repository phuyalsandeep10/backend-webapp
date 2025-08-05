"""team

Revision ID: 20250801_084656
Revises: 20250801_083808
Create Date: 2025-08-01 14:31:57.412288

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_084656"
down_revision: Union[str, Sequence[str], None] = "20250801_083808"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TeamMigration(BaseMigration):

    table_name = "org_teams"

    def __init__(self):
        super().__init__(revision="20250801_084656", down_revision="20250801_083808")
        self.common_columns()
        self.string("name", nullable=False)
        self.string("description", nullable=True)
        self.foreign("organization_id", "sys_organizations")

        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    TeamMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    TeamMigration().downgrade()
