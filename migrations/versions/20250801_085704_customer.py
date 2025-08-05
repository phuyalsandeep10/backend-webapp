"""customer

Revision ID: 20250801_085704
Revises: 20250801_085215
Create Date: 2025-08-01 14:42:05.815483

"""

<<<<<<< HEAD
=======
from httpx._transports import default
from sqlmodel import null
from migrations.base import BaseMigration
>>>>>>> 8c04d2f (customer logs added)
from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "20250801_085704"
down_revision: Union[str, Sequence[str], None] = "20250801_085215"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CustomerMigration(BaseMigration):

    table_name = "org_customers"

    def __init__(self):
        super().__init__(revision="20250801_085704", down_revision="20250801_085215")
        # describe your schemas here
        self.common_columns()
        self.foreign("organization_id", "sys_organizations")
        self.string("name", nullable=True)
        self.string("email", nullable=True)
        self.string("phone", nullable=True)
        self.string("address", nullable=True)
        self.string("ip_address", nullable=False)
        self.boolean('is_online', nullable=False, default=False)
        self.json('attributes',default={},nullable=True)


def upgrade() -> None:
    """
    Function to create a table
    """
    CustomerMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    CustomerMigration().downgrade()
