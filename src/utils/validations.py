from typing import Type, TypeVar

from fastapi import HTTPException

from src.common.context import TenantContext

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
