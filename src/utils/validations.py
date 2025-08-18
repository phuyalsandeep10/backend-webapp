from typing import Any, Dict, Type, TypeVar, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.common.context import TenantContext
from src.common.models import BaseModel, CommonModel

T = TypeVar("T")


class TenantEntityValidator:
    """
    TenantEntityValidator class for entity validation
    """

    def __init__(self):
        organization_id = TenantContext.get()
        self.org_id = organization_id

    async def validate(
        self, model: Type[T], entity_id: int, check_default: bool = False
    ):
        instance = await model.find_one(
            where={"id": entity_id, "organization_id": self.org_id}
        )

        if not instance:
            raise HTTPException(
                status_code=400,
                detail=f"{model.__name__} ID {entity_id} is invalid for this organization.",
            )
        return instance
