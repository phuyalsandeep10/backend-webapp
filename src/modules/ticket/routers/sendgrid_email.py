from typing import Optional

from fastapi import APIRouter, Form, UploadFile
from fastapi.requests import Request

from src.modules.sendgrid.services import get_recent_reply
from src.modules.ticket.services.converstaion import ticket_conversation_service

router = APIRouter()


@router.post("/sendgrid-email-reply")
async def email_reply(
    request: Request,
):
    form = await request.form()

    from_email = form.get("from")
    to_email = form.get("to")
    full_text = form.get("text")
    recent_reply = get_recent_reply(full_text)

    await ticket_conversation_service.save_message_from_email(
        from_email, to_email, recent_reply
    )
