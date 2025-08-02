"""verification

Revision ID: 20250801_020510
Revises: 20250801_015459
Create Date: 2025-08-01 07:50:10.337030

"""

from migrations.base import BaseMigration
from typing import Sequence, Union


revision: str = '20250801_020510'
down_revision: Union[str, Sequence[str], None] = '20250801_015459'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

class VerificationMigration(BaseMigration):

    table_name = "email_verifications"
    def __init__(self):
        super().__init__(revision='20250801_020510',down_revision='20250801_015459')
        self.primary_key()
        self.foreign("user_id", "sys_users", ondelete="CASCADE")
        self.string("token", unique=True, index=True, nullable=False)
        
        self.string("type", default="email_verification", nullable=False)
        self.date_time("expires_at", nullable=False)
        self.boolean("is_used", default=False, nullable=False)
        self.timestamp_columns()
        
        #describe your schemas here


def upgrade() -> None:
  """
  Function to create a table
  """
  VerificationMigration().upgrade()
  

def downgrade() -> None:
  """
  Function to drop a table
  """
  VerificationMigration().downgrade()
