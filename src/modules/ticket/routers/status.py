from typing import List

from fastapi import APIRouter, Depends

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import (
    CreateTicketStatusSchema,
    EditTicketStatusSchema,
    TicketStatusOut,
)
from src.modules.ticket.services.status import ticket_status_service
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.get(
    "/status",
    summary="List all the status",
    response_model=CustomResponseSchema[List[TicketStatusOut]],
)
async def list_ticket_status(user=Depends(get_current_user)):
    """
    List all the priorities defined by the organization
    """
    return await ticket_status_service.list_ticket_status(user)


@router.post("/status", summary="Create a status", response_model=CustomResponseSchema)
async def register_ticket_status(
    payload: List[CreateTicketStatusSchema], user=Depends(get_current_user)
):
    """
    Create priorities for the particular organization
    """
    return await ticket_status_service.create_ticket_status(payload, user)


@router.get(
    "/status/{ticket_status_id:int}",
    summary="List particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def get_ticket_status(ticket_status_id: int, user=Depends(get_current_user)):
    """
    List particular ticket status defined by the organization
    """
    return await ticket_status_service.get_ticket_status(ticket_status_id, user)


@router.patch(
    "/status/{ticket_status_id:int}",
    summary="Edit particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def edit_ticket_status(
    ticket_status_id: int,
    payload: EditTicketStatusSchema,
    user=Depends(get_current_user),
):
    """
    Edit particular ticket status defined by the organization
    """
    return await ticket_status_service.edit_ticket_status(
        ticket_status_id, payload, user
    )


@router.delete(
    "/status/{ticket_status_id:int}",
    summary="Delete particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def delete_ticket_status(ticket_status_id: int, user=Depends(get_current_user)):
    """
    Delete particular ticket status defined by the organization
    """
    return await ticket_status_service.delete_ticket_status(ticket_status_id, user)
