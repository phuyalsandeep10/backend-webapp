
from fastapi import APIRouter
from fastapi import Request

from src.models import Conversation, Customer, CustomerVisitLogs

from src.utils.response import CustomResponse as cr
from src.utils.common import get_location
from ..services.message_service import MessageService
from ..schema import MessageSchema, EditMessageSchema, CustomerUpdateSchema
from src.common.context import UserContext, TenantContext

from src.services.conversation_service import ConversationService

router = APIRouter()


@router.post("")
async def create_customer( request: Request):
    organizationId = TenantContext.get()
    
    header = request.headers.get("X-Forwarded-For")
    organizationId = TenantContext.get()

    ip = header.split(",")[0].strip() if header else request.client.host

    print(f"create customer api {ip}")


    
    


    customer_count = await Customer.sql(
        f"select count(*) from org_customers where organization_id={organizationId}"
    )

    print(f"customer_count {customer_count}")

    customer_count = customer_count[0].get('count')+1

    customer = await Customer.create(
        name=f"guest-{customer_count}", ip_address=ip, organization_id=organizationId
    )


    await save_log(ip, customer.id, request)

    return cr.success(
        data={"customer": customer.to_json()}
    )


async def save_log(ip: str, customer_id: int, request):
    data = {}

    data = await get_location(ip)

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
    print(f"visit api {ip}")
    customer = await Customer.get(customer_id)
    if not customer:
        return cr.error(message="Customer Not found")

    log = await save_log(ip, customer_id, request)

    return cr.success(data=log.to_json())



@router.put("/{customer_id}/update")
async def update_customer(customer_id: int, payload: CustomerUpdateSchema):
    customer = await Customer.get(customer_id)
    if not customer:
        return cr.error(message="Customer Not found")
    customer = await Customer.update(customer_id,**payload.dict(exclude_unset=True))
    return cr.success(data=customer.to_json())




@router.post('/conversations/{conversation_id}/messages')
async def create_conversation_message(conversation_id: int, payload: MessageSchema):
    organizationId = TenantContext.get()
    userId = UserContext.get()
    service = MessageService(organization_id=organizationId, payload=payload,user_id=userId)
    response = await service.create(conversation_id)

    

    return cr.success(data=response)


@router.post('/{customer_id}/initialize-conversation')
async def initialize_conversation(customer_id: int,payload:MessageSchema):
    organizationId = TenantContext.get()
    payload.customer_id = customer_id
    record = await Conversation.create(
        customer_id=customer_id,
        organization_id=organizationId,
    )
    
    # Note: Customer will automatically join the room when they connect to WebSocket
    # via the _join_existing_conversations method in CustomerChatNamespace
    print(f"✅ Created conversation {record.id} for customer {customer_id}")
    
    service = MessageService(organization_id=organizationId, payload=payload)
    message = await service.create(record.id)

    
    return cr.success(data={
        "conversation": record.to_json(),
        "message": message
    })

# edit the message
@router.put("/{organization_id}/messages/{message_id}")
async def edit_message(message_id: int, payload: EditMessageSchema):
    organizationId = TenantContext.get()
    print(f"organizationId {organizationId}")

    userId = UserContext.get()

    service = MessageService(organizationId, payload, userId)
    record = await service.edit(message_id)

    return cr.success(data=record.to_json())

@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int):
    organizationId = TenantContext.get()
    print(f"organizationId {organizationId}")
    print(f"conversation_id {conversation_id}")

   

    record = await Conversation.find_one(
        {"id": conversation_id, "organization_id": organizationId}
    )

    if not record:
        return cr.error(message="Conversation Not found")
    
    
    records = await MessageService(organizationId).get_messages(conversation_id)

    return cr.success(data=records)
