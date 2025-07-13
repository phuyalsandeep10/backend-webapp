from fastapi import APIRouter

from .contact import router as contact_router
from .ticket import router as ticket_router

router = APIRouter(prefix="/ticket")

router.include_router(ticket_router)
router.include_router(contact_router)
