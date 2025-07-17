from typing import Annotated

from fastapi import APIRouter, Header

from src.modules.ticket.schemas import CreateSLASchema
from src.modules.ticket.services.sla import sla_service

router = APIRouter()


@router.post("/sla", summary="Creates new Service Level agreement")
async def register_sla(
    payload: CreateSLASchema, authorization: Annotated[str, Header()]
):
    return await sla_service.register_sla(payload, authorization)


@router.get("/sla", summary="List all Service Level agreements")
async def get_all():
    return await sla_service.get_all_sla()
