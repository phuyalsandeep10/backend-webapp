"""customerlogs

Revision ID: 20250801_085926
Revises: 20250801_085704
Create Date: 2025-08-01 14:44:26.940295

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250801_085926"
down_revision: Union[str, Sequence[str], None] = "20250801_085704"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CustomerlogsMigration(BaseMigration):

    table_name = "org_customer_logs"

    def __init__(self):
        super().__init__(revision="20250801_085926", down_revision="20250801_085704")
        self.common_columns()
        self.foreign("customer_id", "org_customers")
        self.string("ip_address")
        self.string("user_agent")
        self.string("latitude")
        self.string("longitude")
        self.string("country")
    
    
        self.string("city")
        self.string("device")
        self.string("browser")
        self.string("os")
        self.string("device_type")


def upgrade() -> None:
    """
    Function to create a table
    """
    CustomerlogsMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    CustomerlogsMigration().downgrade()
