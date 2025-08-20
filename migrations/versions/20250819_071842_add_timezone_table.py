"""Add Timezone table

Revision ID: 20250819_071842
Revises: 20250819_071631
Create Date: 2025-08-19 07:18:43.237692

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = '20250819_071842'
down_revision: Union[str, Sequence[str], None] = '20250819_071631'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class TimezoneMigration(BaseMigration):

    table_name = "sys_timezones"
    def __init__(self):
        super().__init__(revision='20250810_070640',down_revision='20250810_070453')
        self.create_whole_table=True
        #describe your schemas here
        self.base_columns()
        self.string("name", nullable=False)
        self.string("display_name", nullable=False)
        self.foreign("country_id", "sys_countries", nullable=True)
        #describe your schemas here


def upgrade() -> None:
  """
  Function to create a table
  """
  TimezoneMigration().upgrade()
  

def downgrade() -> None:
  """
  Function to drop a table
  """
  TimezoneMigration().downgrade()
