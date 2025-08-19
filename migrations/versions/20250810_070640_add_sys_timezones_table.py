"""Add sys_timezones table

Revision ID: 20250810_070640
Revises: 20250810_070453
Create Date: 2025-08-10 12:51:41.159272

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = '20250810_070640'
down_revision: Union[str, Sequence[str], None] = '20250810_070453'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class TimezonesMigration(BaseMigration):

    table_name = "sys_timezones"
    def __init__(self):
        super().__init__(revision='20250810_070640',down_revision='20250810_070453')
        self.create_whole_table=True
        #describe your schemas here
        self.base_columns()
        self.string("name", nullable=False)
        self.string("display_name", nullable=False)
        self.foreign("country_id", "sys_countries", nullable=True)

def upgrade() -> None:
  """
  Function to create a table
  """
  TimezonesMigration().upgrade()
  
  # Insert seed data
  timezones_data = [
      {"name": "Asia/Kathmandu", "display_name": "Nepal/Kathmandu", "country_id": 1},
      {"name": "America/New_York", "display_name": "America/New York", "country_id": 2},
      {"name": "America/Los_Angeles", "display_name": "America/Los Angeles", "country_id": 2},
      {"name": "Asia/Kolkata", "display_name": "Asia/Kolkata", "country_id": 3},
      {"name": "America/Toronto", "display_name": "America/Toronto", "country_id": 4},
      {"name": "Europe/London", "display_name": "Europe/London", "country_id": 5},
  ]
  
  TimezonesMigration().bulk_insert_data(rows=timezones_data)


def downgrade() -> None:
  """
  Function to drop a table
  """
  TimezonesMigration().downgrade()
