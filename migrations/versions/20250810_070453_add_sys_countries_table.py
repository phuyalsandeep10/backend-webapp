"""Add sys_countries table

Revision ID: 20250810_070453
Revises: 20250803_053316
Create Date: 2025-08-10 12:49:54.710589

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = '20250810_070453'
down_revision: Union[str, Sequence[str], None] = '20250731_023113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class CountriesMigration(BaseMigration):

    table_name = "sys_countries"
    def __init__(self):
        super().__init__(revision='20250810_070453',down_revision='20250803_053316')
        self.create_whole_table=True
        #describe your schemas here
        self.primary_key()
        self.string("name", nullable=False)
        self.string("iso_code_2", nullable=False, length=2)
        self.string("iso_code_3", nullable=False, length=3)
        self.string("phone_code", nullable=True, length=10)
        self.timestamp_columns()

def upgrade() -> None:
  """
  Function to create a table
  """
  CountriesMigration().upgrade()
  
  # Insert seed data
  countries_data = [
      {"name": "Nepal", "iso_code_2": "NP", "iso_code_3": "NPL", "phone_code": "+977"},
      {"name": "United States", "iso_code_2": "US", "iso_code_3": "USA", "phone_code": "+1"},
      {"name": "India", "iso_code_2": "IN", "iso_code_3": "IND", "phone_code": "+91"},
      {"name": "Canada", "iso_code_2": "CA", "iso_code_3": "CAN", "phone_code": "+1"},
      {"name": "United Kingdom", "iso_code_2": "GB", "iso_code_3": "GBR", "phone_code": "+44"},
  ]
  
  CountriesMigration().bulk_insert_data(rows=countries_data)

def downgrade() -> None:
  """
  Function to drop a table
  """
  CountriesMigration().downgrade()
