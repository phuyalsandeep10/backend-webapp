from typing import List

from fastapi import APIRouter, Depends

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import CreatePrioriySchema, PriorityOut
from src.modules.ticket.services.priority import priority_service
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.get(
    "/priority",
    summary="List all the priorities",
    response_model=CustomResponseSchema[List[PriorityOut]],
)
async def list_priorities(user=Depends(get_current_user)):
    """
    List all the priorities defined by the organization
    """
    return await priority_service.list_priorities(user)


@router.post(
    "/priority", summary="Create a priority", response_model=CustomResponseSchema
)
async def register_priority(
    payload: List[CreatePrioriySchema], user=Depends(get_current_user)
):
    """
    Create priorities for the particular organization
    """
    return await priority_service.create_priorities(payload, user)


@router.get(
    "/priority/{priority_id:int}",
    summary="List particular priority",
    response_model=CustomResponseSchema[PriorityOut],
)
async def get_priority(priority_id: int, user=Depends(get_current_user)):
    """
    List particular priority defined by the organization
    """
    return await priority_service.list_priorities(user)
