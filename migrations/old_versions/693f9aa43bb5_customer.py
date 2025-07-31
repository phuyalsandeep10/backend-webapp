"""customer

Revision ID: 693f9aa43bb5
Revises: 426319c96149
Create Date: 2025-07-03 12:39:13.516732

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa
from migrations.common import common_columns


# revision identifiers, used by Alembic.
revision: str = '693f9aa43bb5'
down_revision: Union[str, Sequence[str], None] = '426319c96149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_customers",
        *common_columns(),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("sys_organizations.id"), nullable=False),
        sa.Column("phone", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("country", sa.String(255), nullable=True),
       
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_customers")
