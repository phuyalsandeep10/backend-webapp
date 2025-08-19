"""Add sys_countries table

Revision ID: 20250810_070453
Revises: 20250803_053316
Create Date: 2025-08-10 12:49:54.710589

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = '20250810_070453'
down_revision: Union[str, Sequence[str], None] = '20250810_054007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class CountriesMigration(BaseMigration):

    table_name = "sys_countries"
    def __init__(self):
        super().__init__(revision='20250810_070453',down_revision='20250803_053316')
        self.create_whole_table=True
        #describe your schemas here
        self.base_columns()
        self.string("name", nullable=False)
        self.string("iso_code_2", nullable=False, length=2)
        self.string("iso_code_3", nullable=False, length=3)
        self.string("phone_code", nullable=True, length=10)

def upgrade() -> None:
  """
  Function to create a table
  """
  CountriesMigration().upgrade()
  
  # Insert seed data
  # In your countries migration file
  countries_data = [
      {"name": "Nepal", "iso_code_2": "NP", "iso_code_3": "NPL", "phone_code": "+977"},
      {"name": "United States", "iso_code_2": "US", "iso_code_3": "USA", "phone_code": "+1"},
      {"name": "France", "iso_code_2": "FR", "iso_code_3": "FRA", "phone_code": "+33"},
      {"name": "Japan", "iso_code_2": "JP", "iso_code_3": "JPN", "phone_code": "+81"},
      {"name": "India", "iso_code_2": "IN", "iso_code_3": "IND", "phone_code": "+91"},
      {"name": "Germany", "iso_code_2": "DE", "iso_code_3": "DEU", "phone_code": "+49"},
      {"name": "Canada", "iso_code_2": "CA", "iso_code_3": "CAN", "phone_code": "+1"},
      {"name": "United Kingdom", "iso_code_2": "GB", "iso_code_3": "GBR", "phone_code": "+44"},
      {"name": "Australia", "iso_code_2": "AU", "iso_code_3": "AUS", "phone_code": "+61"},
      {"name": "China", "iso_code_2": "CN", "iso_code_3": "CHN", "phone_code": "+86"},
      {"name": "Brazil", "iso_code_2": "BR", "iso_code_3": "BRA", "phone_code": "+55"},
      {"name": "Russia", "iso_code_2": "RU", "iso_code_3": "RUS", "phone_code": "+7"},
      {"name": "South Korea", "iso_code_2": "KR", "iso_code_3": "KOR", "phone_code": "+82"},
      {"name": "Italy", "iso_code_2": "IT", "iso_code_3": "ITA", "phone_code": "+39"},
      {"name": "Spain", "iso_code_2": "ES", "iso_code_3": "ESP", "phone_code": "+34"},
      {"name": "Pakistan", "iso_code_2": "PK", "iso_code_3": "PAK", "phone_code": "+92"},
      {"name": "Bangladesh", "iso_code_2": "BD", "iso_code_3": "BGD", "phone_code": "+880"},
      {"name": "United Arab Emirates", "iso_code_2": "AE", "iso_code_3": "ARE", "phone_code": "+971"},
      {"name": "Singapore", "iso_code_2": "SG", "iso_code_3": "SGP", "phone_code": "+65"},
      {"name": "Thailand", "iso_code_2": "TH", "iso_code_3": "THA", "phone_code": "+66"},
      {"name": "Indonesia", "iso_code_2": "ID", "iso_code_3": "IDN", "phone_code": "+62"},
      {"name": "Philippines", "iso_code_2": "PH", "iso_code_3": "PHL", "phone_code": "+63"},
      {"name": "Vietnam", "iso_code_2": "VN", "iso_code_3": "VNM", "phone_code": "+84"},
      {"name": "Egypt", "iso_code_2": "EG", "iso_code_3": "EGY", "phone_code": "+20"},
      {"name": "Mexico", "iso_code_2": "MX", "iso_code_3": "MEX", "phone_code": "+52"},
      {"name": "South Africa", "iso_code_2": "ZA", "iso_code_3": "ZAF", "phone_code": "+27"},
  ]
  
  CountriesMigration().bulk_insert_data(rows=countries_data)

def downgrade() -> None:
  """
  Function to drop a table
  """
  CountriesMigration().downgrade()
