from typing import Annotated, List

from fastapi import APIRouter, Depends, Header, HTTPException

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import (
    CreateTicketSchema,
    FullCreateTicketSchema,
    TicketOut,
)
from src.modules.ticket.services.ticket import ticket_services
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.post("/", summary="Creates new ticket", response_model=CustomResponseSchema)
async def register_ticket(payload: CreateTicketSchema, user=Depends(get_current_user)):
    return await ticket_services.create_ticket(payload, user)


@router.get(
    "/",
    summary="List all tickets",
    response_model=CustomResponseSchema[List[TicketOut]],
)
async def list_tickets(user=Depends(get_current_user)):
    return await ticket_services.list_tickets(user)


@router.get(
    "/{ticket_id:int}",
    summary="Get a ticket",
    response_model=CustomResponseSchema[TicketOut],
)
async def get_ticket(ticket_id: int):
    return await ticket_services.get_ticket(ticket_id)


@router.delete(
    "/{ticket_id:int}", summary="Delete a ticket", response_model=CustomResponseSchema
)
async def delete_ticket(ticket_id: int):
    return await ticket_services.delete_ticket(ticket_id)


@router.post(
    "/full-create",
    summary="Creates new ticket with full credentials",
    response_model=CustomResponseSchema,
)
async def register_full_ticket(
    payload: FullCreateTicketSchema, authorization: Annotated[str, Header()]
):
    return await ticket_services.create_full_ticket(payload, authorization)
