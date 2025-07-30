from typing import List

import sqlalchemy as sa
from alembic import op
from sqlalchemy.exc import OperationalError


class BaseMigration:
    """
    This class acts as a base for every migration files
    """

    # attributes
    table_name: str
    fields: List
    revision: str
    down_revision: str

    def __init__(self, revision: str, down_revision: str):
        self.revision = revision
        self.down_revision = down_revision
        self.fields = []

    def upgrade(self) -> None:
        """
        This function is going to create a table
        """
        if not self.table_name or len(self.fields) == 0:
            raise OperationalError(
                "table name and fields must be set", params=None, orig=None
            )
        op.create_table(self.table_name, *self.fields)

    def downgrade(self) -> None:
        """
        This function is going to drop a table
        """
        if not self.table_name:
            raise OperationalError("table name must be set", params=None, orig=None)
        op.drop_table(self.table_name)

    def integer(self, name: str, **kwargs):
        """
        Returns the SQLALchemy Integer column
        """
        co = sa.Column(name, sa.Integer(), **kwargs)
        self.fields.append(co)

    def string(self, name: str, length=55, **kwargs):
        """
        Returns the SQLALchemy String column
        """
        co = sa.Column(name, sa.String(length=length), **kwargs)
        self.fields.append(co)

    def boolean(self, name: str, **kwargs):
        """
        Returns the SQLALchemy boolean column
        """
        co = sa.Column(name, sa.Boolean(), **kwargs)
        self.fields.append(co)

    def primary_key(self, name: str, **kwargs):
        """
        Returns the SQLALChemy Integer column with primary_key true
        """
        co = sa.Column(name, sa.Integer(), primary_key=True, **kwargs)
        self.fields.append(co)

    def foregin_key(self, name: str, table: str, ondelete=None, **kwargs):
        """
        Returns the SQLAlchemy Integer column with foreign key
        """
        co = sa.Column(
            name, sa.Integer(), sa.ForeignKey(table, ondelete=ondelete), **kwargs
        )
        self.fields.append(co)

    def date_time(self, name: str, **kwargs):
        """
        Returns the SQLALCHEMY DateTime field
        """
        co = sa.Column(name, sa.DateTime, **kwargs)
        self.fields.append(co)

    def timestamp_columns(self):
        """
        Return basic timestamp columns
        """
        self.fields.append(
            self.date_time(
                name="created_at", nullable=False, server_default=sa.func.now()
            )
        )
        self.fields.append(
            self.date_time(
                name="updated_at", nullable=False, server_default=sa.func.now()
            )
        )

    def common_columns(self):
        """
        Returns the common columns used in CommonModel
        """
        self.fields.append(self.primary_key(name="id"))
        self.fields.append(self.boolean(name="active", default=True, nullable=False))
        self.fields.append(
            self.foregin_key(name="created_by_id", table="sys_users.id", nullable=True)
        )
        self.fields.append(
            self.foregin_key(name="updated_by_id", table="sys_users.id", nullable=True)
        )
        self.fields.append(self.date_time(name="deleted_at", nullable=True))
        self.timestamp_columns()
