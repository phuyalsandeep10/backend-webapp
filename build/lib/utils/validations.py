from typing import Type, TypeVar

from fastapi import HTTPException


T = TypeVar("T")


class TenantEntityValidator:
    """
    TenantEntityValidator class for entity validation
    """

    def __init__(self, org_id: int):
        self.org_id = org_id

    async def validate(self, model: Type[T], entity_id: int):
        instance = await model.find_one(
            where={"id": entity_id, "organization_id": self.org_id}
        )
        print("The instancejl", instance)
        if instance is None:
            raise HTTPException(
                status_code=400,
                detail=f"{model.__name__} ID {entity_id} is invalid for this organization.",
            )
        return instance
