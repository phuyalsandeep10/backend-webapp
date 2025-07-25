from typing import Annotated, List

from fastapi import APIRouter, Depends, Header

from src.common.dependencies import get_current_user
from src.modules.ticket.schemas import CreateSLASchema, SLAOut
from src.modules.ticket.services.sla import sla_service
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.post(
    "/sla",
    summary="Creates new Service Level agreement",
    response_model=CustomResponseSchema,
)
async def register_sla(payload: CreateSLASchema, user=Depends(get_current_user)):
    return await sla_service.register_sla(payload, user)


@router.get(
    "/sla",
    summary="List all Service Level agreements",
    response_model=CustomResponseSchema[List[SLAOut]],
)
async def get_all():
    return await sla_service.list_slas()


@router.get(
    "/sla/{sla_id}", summary="Get a SLA", response_model=CustomResponseSchema[SLAOut]
)
async def get_sla(sla_id: int):
    return await sla_service.get_sla(sla_id)


@router.delete(
    "/sla/{sla_id}", summary="Delete a SLA", response_model=CustomResponseSchema
)
async def delete_sla(sla_id: int):
    return await sla_service.delete_sla(sla_id)
