"""status table added

Revision ID: ea8c22fe9b79
Revises: 0d37df01ec47
Create Date: 2025-07-24 16:23:56.515786

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea8c22fe9b79"
down_revision: Union[str, Sequence[str], None] = "0d37df01ec47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ticket_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("is_default", sa.Boolean(), default=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["sys_organizations.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("organization_id", "name", name="uniq_org_status_name"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.op.drop_table("ticket_status")
