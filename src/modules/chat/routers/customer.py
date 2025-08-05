from fastapi import APIRouter
from fastapi import Request, Header, Depends
 
from src.common.dependencies import get_current_user
from src.models import Conversation, Customer, CustomerVisitLogs
from src.utils.response import CustomResponse as cr
from src.utils.common import get_location

router = APIRouter()


@router.post("/{organizationId}")
async def create_customer(organizationId: int, request: Request):
    header = request.headers.get("X-Forwarded-For")
    

    ip = header.split(",")[0].strip() if header else request.client.host
    customer_count = await Customer.sql(f"select count(*) from org_customers where organization_id={organizationId}")
    customer_count += 1
    print(f"Customer count: {customer_count}")

    customer = await Customer.create(
        name=f"guest-{customer_count}", ip_address=ip, organization_id=organizationId
    )

    conversation = await Conversation.create(
        name=f"guest-{customer_count}",
        customer_id=customer.id,
        ip_address=ip,
        organization_id=organizationId,
    )

    await save_log(ip, customer.id, request)

    return {"customer": customer, "conversation": conversation}




async def save_log(ip: str, customer_id: int, request):
    data = {}

    data = await get_location(ip)
    print(f"Location data: {data}") 

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
        # referral_from=request.headers.get("Referer") or None,
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

    return cr.success(data=customers)
