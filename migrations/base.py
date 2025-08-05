from typing import List

import sqlalchemy as sa
from alembic import op
from sqlalchemy.exc import OperationalError
from sqlmodel import ForeignKey


class BaseMigration:
    """
    This class acts as a base for every migration files
    """

    # attributes
    table_name: str
    fields: List
    added_column: List
    create_new_table: bool
    revision: str
    down_revision: str

    def __init__(self, revision: str, down_revision: str):
        self.revision = revision
        self.down_revision = down_revision
        self.fields = []
        self.added_column = []
        self.create_whole_table = True  # by default set the create table true

    def add_column(self, col: sa.Column):
        """
        This function is used to add column
        """
        self.added_column.append(col)

    def upgrade(self) -> None:
        """
        This function is going to create a table
        """
        if not self.table_name or len(self.fields) == 0:
            raise OperationalError(
                "table name and fields must be set", params=None, orig=None
            )
        if self.create_whole_table:
            op.create_table(self.table_name, *self.fields)
            return None

        for col in self.added_column:
            op.add_column(self.table_name, col)
        return None

    def downgrade(self) -> None:
        """
        This function is going to drop a table
        """
        if not self.table_name:
            raise OperationalError("table name must be set", params=None, orig=None)
        if self.create_whole_table:
            op.drop_table(self.table_name)
            return None

        for col in reversed(self.added_column):  # FIFO
            op.drop_column(self.table_name, col.name)
        return None

    def integer(self, name: str, **kwargs):
        """
        Returns the SQLALchemy Integer column
        """
        co = sa.Column(name, sa.Integer(), **kwargs)
        self.fields.append(co)
        return co

    def biginteger(self, name: str, **kwargs):
        """
        Returns the SQLALchemy BigInteger column
        """
        co = sa.Column(name, sa.BigInteger(), **kwargs)
        self.fields.append(co)
        return co

    def string(self, name: str, length=255, nullable=True, default=None, **kwargs):
        """
        Returns the SQLALchemy String column
        """
        co = sa.Column(
            name, sa.String(length=length), nullable=nullable, default=default, **kwargs
        )
        self.fields.append(co)
        return co

    def boolean(self, name: str, **kwargs):
        """
        Returns the SQLALchemy boolean column
        """
        co = sa.Column(name, sa.Boolean(), **kwargs)
        self.fields.append(co)
        return co

    def json(self, name: str, **kwargs):
        """
        Returns the SQLALchemy JSON column
        """
        co = sa.Column(name, sa.JSON(), **kwargs)
        self.fields.append(co)

    def primary_key(self, name: str = "id", **kwargs):
        """
        Returns the SQLALChemy Integer column with primary_key true
        """
        co = sa.Column(name, sa.Integer(), primary_key=True, **kwargs)
        self.fields.append(co)
        return co

    def foreign(self, name: str, table: str, ondelete=None, **kwargs):
        """
        Returns the SQLAlchemy Integer column with foreign key
        """
        kwargs.setdefault("nullable", True)
        # kwargs.setdefault("index", True)
        table = f"{table}.id"  # by default it will be id
        co = sa.Column(
            name,
            sa.Integer(),
            sa.ForeignKey(table, ondelete=ondelete),
            **kwargs,
        )
        self.fields.append(co)
        return co

    def date_time(self, name: str, **kwargs):
        """
        Returns the SQLALCHEMY DateTime field
        """
        co = sa.Column(name, sa.DateTime, **kwargs)
        self.fields.append(co)
        return co

    def unique_constraint(self, *columns):
        """
        Returns the unique constraint
        """

        co = sa.UniqueConstraint(*columns)
        self.fields.append(co)
        return co

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

    def base_columns(self):
        """
        Return basic model columns
        """
        self.fields.append(self.primary_key(name="id"))
        self.timestamp_columns()

    def common_columns(self):
        """
        Returns the common columns used in CommonModel
        """
        self.fields.append(self.primary_key(name="id"))
        self.fields.append(self.boolean(name="active", default=True, nullable=False))
        self.fields.append(
            self.foreign(name="created_by_id", table="sys_users", key="created_by_id")
        )
        self.fields.append(
            self.foreign(name="updated_by_id", table="sys_users", key="updated_by_id")
        )
        self.fields.append(self.date_time(name="deleted_at", nullable=True))
        self.timestamp_columns()

    def tenant_columns(self):
        """
        Returns the tenant columns used in TenantModel
        """
        self.common_columns()
        self.fields.append(
            self.foreign(name="organization_id", table="sys_organizations")
        )

    def bulk_insert_data(self, rows: List[dict]):
        """
        Insert multiple rows into the table using bulk_insert.
        Dynamically constructs the table using current fields.
        """

        if not self.table_name:
            raise OperationalError("table name must be set", params=None, orig=None)
        if not rows or not isinstance(rows, list):
            raise ValueError(
                "bulk_insert_data requires a non-empty list of dictionaries"
            )

        # Create a table representation for insert
        metadata = sa.MetaData()
        cols = [col for col in self.fields if isinstance(col, sa.Column)]
        table = sa.Table(self.table_name, metadata, *cols)

        op.bulk_insert(table, rows)
