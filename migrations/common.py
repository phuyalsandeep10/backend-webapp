import sqlalchemy as sa


def timestamp_columns():
    return [
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    ]


def common_columns():
    return [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column(
            "created_by_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=True
        ),
        sa.Column(
            "updated_by_id", sa.Integer, sa.ForeignKey("sys_users.id"), nullable=True
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        *timestamp_columns(),
    ]


def base_columns():
    return [sa.Column("id", sa.Integer, primary_key=True), *timestamp_columns()]

