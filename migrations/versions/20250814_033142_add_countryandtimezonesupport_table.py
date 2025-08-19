"""Add CountryAndTimeZoneSupport table

Revision ID: 20250814_033142
Revises: 20250810_070640
Create Date: 2025-08-14 09:16:47.007392

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250814_033142"
down_revision: Union[str, Sequence[str], None] = "20250810_070640"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CountryAndTimeZoneSupportMigration(BaseMigration):

    table_name = "sys_organizations"

    def __init__(self):
        super().__init__(revision="20250814_033142", down_revision="20250810_070640")
        self.create_whole_table = False
        self.add_column(self.foreign("country_id", "sys_countries"))
        self.add_column(self.foreign("timezone_id", "sys_timezones"))
        # describe your schemas here


def upgrade() -> None:
    """
    Function to create a table
    """
    CountryAndTimeZoneSupportMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    CountryAndTimeZoneSupportMigration().downgrade()
