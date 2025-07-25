from typing import List

from fastapi import APIRouter, Depends

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import CreatePrioriySchema
from src.modules.ticket.services.priority import priority_service

router = APIRouter()


@router.get("/priority", summary="List all the priorities")
async def list_priorities(user=Depends(get_current_user)):
    """
    List all the priorities defined by the organization
    """
    return await priority_service.list_priorities(user)


@router.post("/priority", summary="Create a priority")
async def register_priority(
    payload: List[CreatePrioriySchema], user=Depends(get_current_user)
):
    """
    Create priorities for the particular organization
    """
    return await priority_service.create_priorities(payload, user)


@router.get("/priority/{priority_id:int}", summary="List particular priority")
async def get_priority(priority_id: int, user=Depends(get_current_user)):
    """
    List particular priority defined by the organization
    """
    return await priority_service.list_priorities(user)


@router.delete("/priority/{priority_id:int}", summary="Delete particular priority")
async def delete_priority(priority_id: int, user=Depends(get_current_user)):
    """
    delete particular priority defined by the organization
    """
    return await priority_service.list_priorities(user)
