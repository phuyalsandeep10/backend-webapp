import httpx
from fastapi import APIRouter, Depends, FastAPI, Header, Request

from src.common.dependencies import get_current_user
from src.models import Conversation, Customer
from src.utils.response import CustomResponse as cr

router = APIRouter()


@router.post("/{organizationId}")
async def create_customer(organizationId: int, request: Request):
    header = request.headers.get("X-Forwarded-For")
    ip = header.split(",")[0].strip() if header else request.client.host
    customer = await Customer.create(
        name=f"{ip}-customer",
        ip_address=ip,
        organization_id=organizationId,
        email="rajivmahato@customer.com",
    )

    conversation = await Conversation.create(
        name=f"{ip}-Conversation",
        customer_id=customer.id,
        ip_address=ip,
        organization_id=organizationId,
    )
    return cr.success(
        data={"customer": customer.to_json(), "conversation": conversation.to_json()}
    )


@router.get("")
async def get_customers(organizationId: int, user=Depends(get_current_user)):

    customers = await Customer.filter(where={"organization_id": organizationId})

    return cr.success(data=[cus.to_json() for cus in customers])
