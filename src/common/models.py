import json
from datetime import datetime
from typing import Any, List, Optional, Type, TypeVar, Union

import sqlalchemy as sa
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import and_, inspect, or_
from sqlalchemy.orm import Load, selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlmodel import Column, Field, ForeignKey, SQLModel, select

from src.common.context import TenantContext, UserContext
from src.db.config import async_session

T = TypeVar("T")


def case_insensitive(attributes):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            async with async_session() as session:
                statement = select(type(self))
                for key, value in kwargs.items():
                    if key in attributes:
                        statement = statement.where(
                            func.lower(getattr(type(self), key)) == value.lower()
                        )
                    else:
                        statement = statement.where(getattr(type(self), key) == value)
                result = await session.execute(statement)
                return result.scalars().all()

        return wrapper

    return decorator


class BaseModel(SQLModel):
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def to_json(self, schema: Optional[Type[PydanticBaseModel]] = None) -> dict:
        try:
            if schema:
                field_names = set(schema.model_fields.keys())  # Pydantic v2
                return json.loads(self.model_dump_json(include=field_names))
            return json.loads(self.model_dump_json())
        except Exception as e:
            raise e

    @classmethod
    async def get(cls: Type[T], id: int) -> Optional[T]:
        async with async_session() as session:
            return await session.get(cls, id)

    @classmethod
    async def first(cls: Type[T], where: Optional[dict] = None) -> Optional[T]:
        async with async_session() as session:
            statement = select(cls)
            if where is not None:
                if "deleted_at" in inspect(cls).columns:  # type:ignore
                    where.setdefault("deleted_at", None)
            statement = query_statement(cls, where=where)
            result = await session.execute(statement)
            return result.scalars().first() if result else None

    @classmethod
    async def get_all(
        cls: Type[T],
        where: Optional[dict] = None,
        related_items: Optional[Union[_AbstractLoad, list[_AbstractLoad]]] = None,
    ) -> List[T]:
        async with async_session() as session:
            if where is not None:
                if "deleted_at" in inspect(cls).columns:  # type:ignore
                    where.setdefault("deleted_at", None)
            statement = query_statement(cls, where=where)
            if related_items:
                # related_items can be a single selectinload() or a list of them
                if isinstance(related_items, list):
                    for item in related_items:
                        statement = statement.options(item)
                else:
                    statement = statement.options(related_items)
            result = await session.execute(statement)
            return list(result.scalars().all())

    @classmethod
    async def create(cls: Type[T], **kwargs) -> T:
        async with async_session() as session:
            obj = cls(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def update(cls: Type[T], id: int, **kwargs) -> Optional[T]:
        async with async_session() as session:
            obj = await session.get(cls, id)
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
            return obj

    @classmethod
    async def delete(cls: Type[T], where: Optional[dict] = None) -> None:
        async with async_session() as session:
            statement = query_statement(
                cls,
                where=where,
            )
            result = await session.execute(statement)
            obj = result.scalars().first()
            if obj:
                await session.delete(obj)
                await session.commit()

    @classmethod
    async def soft_delete(cls: Type[T], where: Optional[dict] = None) -> None:
        """
        This function is used for soft delete by setting the current time at deleted_at field
        """
        async with async_session() as session:
            statement = query_statement(
                cls,
                where=where,
            )
            result = await session.execute(statement)
            obj = result.scalars().first()
            if obj:
                obj.deleted_at = datetime.now()
                session.add(obj)

                await session.commit()
                await session.refresh(obj)

    @classmethod
    async def filter(
        cls: Type[T],
        where: dict = {},
        skip: int = 0,
        limit: Optional[int] = None,
        joins: Optional[list[Any]] = None,
        options: Optional[list[Any]] = None,
        related_items: Optional[Union[_AbstractLoad, list[_AbstractLoad]]] = None,
    ) -> List[T]:
        if "deleted_at" in inspect(cls).columns:  # type:ignore
            where.setdefault("deleted_at", None)
        statement = query_statement(cls, where=where, joins=joins, options=options)
        if skip:
            statement = statement.offset(skip)
        if limit is not None:
            statement = statement.limit(limit)
        if related_items:
            # related_items can be a single selectinload() or a list of them
            if isinstance(related_items, list):
                for item in related_items:
                    statement = statement.options(item)
            else:
                statement = statement.options(related_items)
        async with async_session() as session:
            result = await session.execute(statement)
            return list(result.scalars().all()) if result else []

    @classmethod
    async def find_one(
        cls: Type[T],
        where: dict = {},
        joins: Optional[list[Any]] = None,
        options: Optional[list[Any]] = None,
        related_items: Optional[Union[_AbstractLoad, list[_AbstractLoad]]] = None,
    ) -> Optional[T]:
        if where is not None:
            if "deleted_at" in inspect(cls).columns:  # type:ignore
                where.setdefault("deleted_at", None)
        statement = query_statement(cls, where=where, joins=joins, options=options)
        if related_items:
            # related_items can be a single selectinload() or a list of them
            if isinstance(related_items, list):
                for item in related_items:
                    statement = statement.options(item)
            else:
                statement = statement.options(related_items)
        async with async_session() as session:
            result = await session.execute(statement)
            return result.scalars().first() if result else None


class CommonModel(BaseModel):
    active: bool = Field(default=True)
    created_by_id: int = Field(foreign_key="sys_users.id", nullable=False)
    updated_by_id: int = Field(foreign_key="sys_users.id", nullable=False)
    deleted_at: Optional[datetime] = None

    # arbitrary_types_allowed = True


def query_statement(
    cls: Type[T],
    where: Optional[dict] = None,
    joins: Optional[list[Any]] = None,
    options: Optional[list[Any]] = None,
):
    """Builds a SQLAlchemy select statement for the given model."""
    statement = select(cls)
    if joins:
        for join_model in joins:
            statement = statement.join(join_model)
    if options:
        for opt in options:
            statement = statement.options(opt)
    if where:
        where_expr = parse_where(cls, where)
        if where_expr is not None:
            statement = statement.where(where_expr)
    return statement


def parse_where(cls, where_dict):
    if not where_dict:
        return None
    expressions = []

    for key, value in where_dict.items():
        if key == "OR" and isinstance(value, list):
            # Handle OR conditions
            or_conditions = [
                c for c in (parse_where(cls, cond) for cond in value) if c is not None
            ]
            if or_conditions:
                expressions.append(or_(*or_conditions))

        elif key == "AND" and isinstance(value, list):
            # Handle AND conditions
            and_conditions = [
                c for c in (parse_where(cls, cond) for cond in value) if c is not None
            ]
            if and_conditions:
                expressions.append(and_(*and_conditions))

        elif isinstance(value, dict):

            if "mode" in value:
                if value["mode"] == "insensitive":
                    # Handle case-insensitive conditions
                    col = getattr(cls, key)
                    expressions.append(sa.func.lower(col) == value["value"].lower())
                    continue

            # Support for contains, gt, lt, etc.

            for op, v in value.items():

                col = getattr(cls, key)

                if op == "contains":
                    expressions.append(getattr(cls, key).ilike(f"%{v}%"))

                elif op == "icontains":
                    expressions.append(sa.func.lower(col).contains(v.lower()))

                elif op == "startswith":
                    expressions.append(col.startswith(v))

                elif op == "istartswith":
                    expressions.append(sa.func.lower(col).startswith(v.lower()))

                elif op == "endswith":
                    expressions.append(col.endswith(v))

                elif op == "iendswith":
                    expressions.append(sa.func.lower(col).endswith(v.lower()))

                elif op == "gt":
                    expressions.append(getattr(cls, key) > v)
                elif op == "lt":
                    expressions.append(getattr(cls, key) < v)
                elif op == "gte":
                    expressions.append(getattr(cls, key) >= v)
                elif op == "lte":
                    expressions.append(getattr(cls, key) <= v)
                elif op == "ne":
                    expressions.append(getattr(cls, key) != v)
                else:
                    raise ValueError(f"Unsupported operator: {op}")
        else:
            # Handle simple equality conditions
            expressions.append(getattr(cls, key) == value)
    return and_(*expressions) if expressions else None


class Permission(BaseModel, table=True):
    __tablename__ = "sys_permissions"  # type:ignore
    name: str = Field(max_length=255, nullable=False, index=True)
    identifier: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        table_name = "sys_permissions"


class TenantModel(CommonModel):
    """
    A simple tenant base model for operations related to the organization/tenant
    """

    organization_id: Optional[int] = Field(
        default=None, foreign_key="sys_organizations.id"
    )

    @classmethod
    async def create(cls: Type[T], **kwargs) -> T:
        organization_id = TenantContext.get()
        user_id = UserContext.get()
        kwargs.setdefault("organization_id", organization_id)
        kwargs.setdefault("created_by_id", user_id)

        obj = await super().create(**kwargs)
        return obj

    @classmethod
    async def filter(
        cls: Type[T],
        where: dict = {},
        skip: int = 0,
        limit: Optional[int] = None,
        joins: Optional[list[Any]] = None,
        options: Optional[list[Any]] = None,
        related_items: Optional[Union[_AbstractLoad, list[_AbstractLoad]]] = None,
    ):
        organization_id = TenantContext.get()
        if organization_id:
            where.setdefault("organization_id", organization_id)

        print("Here is", where)

        return await super().filter(where, skip, limit, joins, options, related_items)

    @classmethod
    async def find_one(
        cls: Type[T],
        where: dict = {},
        joins: Optional[list[Any]] = None,
        options: Optional[list[Any]] = None,
        related_items: Optional[Union[_AbstractLoad, list[_AbstractLoad]]] = None,
    ) -> Optional[T]:
        organization_id = TenantContext.get()
        if organization_id:
            where.setdefault("organization_id", organization_id)

        return await super().find_one(where, joins, options, related_items)

    @classmethod
    async def update(cls: Type[T], id: int, **kwargs) -> Optional[T]:
        organization_id = TenantContext.get()
        user_id = UserContext.get()
        kwargs.setdefault("organization_id", organization_id)
        kwargs.setdefault("updated_by_id", user_id)
        return await super().update(id, **kwargs)
