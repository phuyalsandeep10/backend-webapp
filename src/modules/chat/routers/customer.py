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

    customer = await Customer.find_one(
        where={"organization_id": organizationId, "ip_address": ip}
    )
    if customer:
        await save_log(ip, customer.id, request)
        conversation = await Conversation.find_one(where={"customer_id": customer.id})

        return cr.success(
            data={
                "customer": customer.to_json(),
                "conversation": conversation.to_json(),
            }
        )

    customer_count = await Customer.sql(
        f"select count(*) from org_customers where organization_id={organizationId}"
    )
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
    print(f"Customer: {customer}")
    print(f"Conversation: {conversation}")

    return cr.success(
        data={"customer": customer.to_json(), "conversation": conversation.to_json()}
    )


async def save_log(ip: str, customer_id: int, request):
    data = {}

    data = await get_location(ip)
    print(f"Location data: {data}")

    city = data.get("city")
    country = data.get("country")
    latitude = data.get("lat")
    longitude = data.get("lon")

    user_agent = request.headers.get("User-Agent", "")
    browser = user_agent.split(" ")[0]
    os = user_agent.split(" ")[1]
    device_type = user_agent.split(" ")[2]
    device = user_agent.split(" ")[3]
    referral_from = request.headers.get("Referer") or None

    print(f"Browser: {browser}")
    print(f"OS: {os}")
    print(f"Device type: {device_type}")
    print(f"Device: {device}")
    print(f"User agent: {user_agent}")
    print(f"Referral from: {request.headers.get('Referer')}")
    print(f"Customer Id {customer_id}")
    print(f"IP: {ip}")

    log = await CustomerVisitLogs.create(
        customer_id=customer_id,
        ip_address=ip,
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
        device=device,
        browser=browser,
        os=os,
        device_type=device_type,
        referral_from=referral_from,
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

    return cr.success(data=log.to_json())


@router.get("")
async def get_customers(organizationId: int, user=Depends(get_current_user)):

    customers = await Customer.filter(where={"organization_id": organizationId})
    new_customers = [cus.to_json() for cus in customers]

    return cr.success(data=new_customers)
