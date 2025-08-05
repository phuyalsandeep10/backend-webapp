import httpx
from fastapi import APIRouter, Depends, FastAPI, Header, Request

from src.common.dependencies import get_current_user
<<<<<<< HEAD
from src.models import Conversation, Customer
=======
from src.models import Conversation, Customer, CustomerVisitLogs
>>>>>>> ebab2db (fixed issue)
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


async def save_log(ip: str, customer_id: int, request):
    data = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()

    city = data.get("city")
    country = data.get("country")
    latitude = data.get("lat")
    longitude = data.get("lon")

    log = await CustomerVisitLogs.create(
        customer_id=customer_id,
        ip_address=ip,
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
        device=request.headers.get("User-Agent", ""),
        referral_from=request.headers.get("Referer") or None,
    )

    return log


@router.post("/{customer_id}/visit")
async def customer_visit(customer_id: int, request: Request):
    header = request.headers.get("X-Forwarded-For")
    ip = header.split(",")[0].strip() if header else request.client.host

    customer = await Customer.get(customer_id)
    if not customer:
        return cr.error(message="Customer Not found")

    log = await save_log(ip, customer_id, request)

    return cr.success(log)


@router.get("")
async def get_customers(organizationId: int, user=Depends(get_current_user)):

    customers = await Customer.filter(where={"organization_id": organizationId})

    return cr.success(data=[cus.to_json() for cus in customers])
