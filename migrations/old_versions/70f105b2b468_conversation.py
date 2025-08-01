"""conversation

Revision ID: 70f105b2b468
Revises: 693f9aa43bb5
Create Date: 2025-07-03 12:45:03.327177

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa
from migrations.common import common_columns

# revision identifiers, used by Alembic.
revision: str = '70f105b2b468'
down_revision: Union[str, Sequence[str], None] = '693f9aa43bb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_conversations",
        *common_columns(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("sys_organizations.id"), nullable=False),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("org_customers.id"), nullable=False),
        sa.Column("ip_address", sa.String(255), nullable=True),
        sa.Column('feeback',sa.String(255),nullable=True),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('org_conversations')
