"""Add OrgTimezone table

Revision ID: 20250819_072251
Revises: 20250819_071842
Create Date: 2025-08-19 07:22:51.749015

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250819_072251"
down_revision: Union[str, Sequence[str], None] = "20250819_071842"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class OrgTimezoneMigration(BaseMigration):
    table_name = "sys_organizations"

    def __init__(self):
        super().__init__(revision="20250819_072251", down_revision="20250819_071842")
        self.create_whole_table = False
        self.add_column(self.foreign("country_id", "sys_countries"))
        self.add_column(self.foreign("timezone_id", "sys_timezones"))


def upgrade() -> None:
    """
    Function to create a table
    """
    OrgTimezoneMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    OrgTimezoneMigration().downgrade()
