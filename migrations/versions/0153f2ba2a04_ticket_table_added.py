"""ticket table added

Revision ID: 0153f2ba2a04
Revises: 569993d68ff6
Create Date: 2025-07-20 09:21:27.745427

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0153f2ba2a04"
down_revision: Union[str, Sequence[str], None] = "569993d68ff6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum(
                "CRITICAL", "HIGH", "MEDIUM", "LOW", "TRIVIAL", name="priorityenum"
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("OPEN", "PENDING", "CLOSED", name="statusenum"),
            nullable=False,
        ),
        sa.Column("issued_by", sa.Integer(), nullable=False),
        sa.Column("sla_id", sa.Integer(), nullable=True),
        sa.Column("contact_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sla_id"], ["sla.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tickets")
