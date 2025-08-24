from typing import List

from fastapi import APIRouter, Depends

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import (
    CreateTicketSchema,
    EditTicketSchema,
    TicketByStatusSchema,
    TicketOut,
)
from src.modules.ticket.services.ticket import ticket_services
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.post("/", summary="Creates new ticket", response_model=CustomResponseSchema)
async def register_ticket(payload: CreateTicketSchema, user=Depends(get_current_user)):
    """
    Register new ticket to the organization
    """
    return await ticket_services.create_ticket(payload, user)


@router.get(
    "/",
    summary="List all tickets",
    response_model=CustomResponseSchema[List[TicketOut]],
)
async def list_tickets():
    """
    List all the tickets of the organization
    """
    return await ticket_services.list_tickets()


@router.post(
    "/by-status",
    summary="List tickets by status",
    response_model=CustomResponseSchema[List[TicketOut]],
)
async def list_tickets_by_status(
    payload: TicketByStatusSchema, user=Depends(get_current_user)
):
    """
    List all the tickets of the organization by id
    """
    return await ticket_services.list_tickets_by_status(payload)


@router.get(
    "/{ticket_id:int}",
    summary="Get a ticket",
    response_model=CustomResponseSchema[TicketOut],
)
async def get_ticket(ticket_id: int, user=Depends((get_current_user))):
    """
    Get ticket of the organization by id
    """
    return await ticket_services.get_ticket(ticket_id, user)


@router.patch(
    "/{ticket_id:int}",
    summary="Get a ticket",
    response_model=CustomResponseSchema[TicketOut],
)
async def edit_ticket(
    ticket_id: int, payload: EditTicketSchema, user=Depends((get_current_user))
):
    """
    Edit ticket of the organization by id
    """
    return await ticket_services.edit_ticket(ticket_id, payload, user)


@router.delete(
    "/{ticket_id:int}", summary="Delete a ticket", response_model=CustomResponseSchema
)
async def delete_ticket(ticket_id: int):
    """
    Delete ticket of the organiation by id
    """
    return await ticket_services.delete_ticket(ticket_id)


@router.get(
    "/confirm/{ticket_id:int}/{confirmation_token:str}",
    response_model=CustomResponseSchema,
)
async def confirm_ticket(ticket_id: int, confirmation_token: str):
    """
    Confirmt the ticket and set status to open defined by the organization
    """
    return await ticket_services.confirm_ticket(ticket_id, token=confirmation_token)
