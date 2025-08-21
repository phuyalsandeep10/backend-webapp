from typing import List

from fastapi import APIRouter

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
async def list_ticket_status():
    """
    List all the priorities defined by the organization
    """
    return await ticket_status_service.list_ticket_status()


@router.post("/status", summary="Create a status", response_model=CustomResponseSchema)
async def register_ticket_status(payload: List[CreateTicketStatusSchema]):
    """
    Create priorities for the particular organization
    """
    return await ticket_status_service.create_ticket_status(payload)


@router.get(
    "/status/{ticket_status_id:int}",
    summary="List particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def get_ticket_status(ticket_status_id: int):
    """
    List particular ticket status defined by the organization
    """
    return await ticket_status_service.get_ticket_status(ticket_status_id)


@router.patch(
    "/status/{ticket_status_id:int}",
    summary="Edit particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def edit_ticket_status(
    ticket_status_id: int,
    payload: EditTicketStatusSchema,
):
    """
    Edit particular ticket status defined by the organization
    """
    return await ticket_status_service.edit_ticket_status(ticket_status_id, payload)


@router.delete(
    "/status/{ticket_status_id:int}",
    summary="Delete particular status",
    response_model=CustomResponseSchema[TicketStatusOut],
)
async def delete_ticket_status(ticket_status_id: int):
    """
    Delete particular ticket status defined by the organization
    """
    return await ticket_status_service.delete_ticket_status(ticket_status_id)
