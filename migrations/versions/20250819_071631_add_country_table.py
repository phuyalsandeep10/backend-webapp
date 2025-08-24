"""Add Country table

Revision ID: 20250819_071631
Revises: 20250814_095326
Create Date: 2025-08-19 07:16:32.241742

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "20250819_071631"
down_revision: Union[str, Sequence[str], None] = "20250819_051645"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CountryMigration(BaseMigration):
    table_name = "sys_countries"

    def __init__(self):
        super().__init__(revision="20250810_070453", down_revision="20250819_051645")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.string("name", nullable=False)
        self.string("iso_code_2", nullable=False, length=2)
        self.string("iso_code_3", nullable=False, length=3)
        self.string("phone_code", nullable=True, length=10)


def upgrade() -> None:
    """
    Function to create a table
    """
    CountryMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    CountryMigration().downgrade()
