from fastapi import APIRouter

from .ticket import router as ticket_router

router = APIRouter(prefix="/ticket")

router.include_router(ticket_router)
