from fastapi import APIRouter

from .contact import router as contact_router
from .sla import router as sla_router
from .ticket import router as ticket_router

router = APIRouter(prefix="/tickets")

router.include_router(ticket_router)
router.include_router(contact_router)
router.include_router(sla_router)
