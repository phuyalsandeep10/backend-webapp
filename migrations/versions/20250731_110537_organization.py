"""organization

Revision ID: 20250731_110537
Revises: 20250731_023113
Create Date: 2025-07-31 16:50:38.279958

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = '20250731_110537'
down_revision: Union[str, Sequence[str], None] = '20250731_023113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class OrganizationMigration(BaseMigration):

    table_name = ""
    def __init__(self):
        super().__init__(revision='20250731_110537',down_revision='20250731_023113')
        #describe your schemas here


def upgrade() -> None:
  """
  Function to create a table
  """
  OrganizationMigration().upgrade()
  

def downgrade() -> None:
  """
  Function to drop a table
  """
  OrganizationMigration().downgrade()
