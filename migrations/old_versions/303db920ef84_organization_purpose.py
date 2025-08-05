"""organization purpose

Revision ID: 303db920ef84
Revises: dccc09a8929f
Create Date: 2025-07-23 16:11:35.107615

"""

from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "303db920ef84"
down_revision: Union[str, Sequence[str], None] = "dccc09a8929f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "org_customer_visit_logs",
        sa.Column("ip_address", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("device", sa.String(length=300), nullable=True),
        sa.Column("os", sa.String(length=100), nullable=True),
        sa.Column("browser", sa.String(length=100), nullable=True),
        sa.Column("device_type", sa.String(length=50), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("referral_from", sa.String(length=300), nullable=True),
        sa.Column("join_at", sa.DateTime(), nullable=False),
        sa.Column("left_at", sa.DateTime(), nullable=True),
        sa.Column("customer_id", sa.ForeignKey("org_customers.id"), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("org_customer_visit_logs")
