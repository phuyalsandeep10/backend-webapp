from typing import List

from fastapi import APIRouter, Depends

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import (
    CreatePrioriySchema,
    EditTicketPrioritySchema,
    PriorityOut,
)
from src.modules.ticket.services.priority import priority_service
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.get(
    "/priority",
    summary="List all the priorities",
    response_model=CustomResponseSchema[List[PriorityOut]],
)
async def list_priorities():
    """
    List all the priorities defined by the organization
    """
    return await priority_service.list_priorities()


@router.post(
    "/priority", summary="Create a priority", response_model=CustomResponseSchema
)
async def register_priority(payload: list[CreatePrioriySchema]):
    """
    Create priorities for the particular organization
    """
    return await priority_service.create_priorities(payload)


@router.get(
    "/priority/{priority_id:int}",
    summary="List particular priority",
    response_model=CustomResponseSchema[PriorityOut],
)
async def get_priority(priority_id: int):
    """
    List particular priority defined by the organization
    """
    return await priority_service.get_priority(priority_id)


@router.patch(
    "/priority/{priority_id:int}",
    summary="Edit particular priority",
    response_model=CustomResponseSchema[PriorityOut],
)
async def edit_priority(priority_id: int, payload: EditTicketPrioritySchema):
    """
    Edit particular priority defined by the organization
    """
    return await priority_service.edit_priority(priority_id, payload)


@router.delete(
    "/priority/{priority_id:int}",
    summary="Delete particular priority",
    response_model=CustomResponseSchema,
)
async def delete_priority(priority_id: int):
    """
    Delete particular priority defined by the organization
    """
    return await priority_service.delete_priority(priority_id)
