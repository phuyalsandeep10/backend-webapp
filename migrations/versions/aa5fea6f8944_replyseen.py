"""replyseen

Revision ID: aa5fea6f8944
Revises: 0551e46b3c51
Create Date: 2025-07-27 15:59:58.249375

"""

from typing import Sequence, Union
import sqlmodel.sql.sqltypes


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa5fea6f8944"
down_revision: Union[str, Sequence[str], None] = "0551e46b3c51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the two new boolean columns
    op.add_column(
        "org_messages",
        sa.Column(
            "seen", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )

    # Add reply_to_id column
    op.add_column("org_messages", sa.Column("reply_to_id", sa.Integer(), nullable=True))

    # Create foreign key constraint
    op.create_foreign_key(
        "fk_org_messages_reply_to_id_org_messages",
        "org_messages",
        "org_messages",
        ["reply_to_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_org_messages_reply_to_id_org_messages", "org_messages", type_="foreignkey"
    )
    op.drop_column("org_messages", "reply_to_id")
    op.drop_column("org_messages", "seen")
