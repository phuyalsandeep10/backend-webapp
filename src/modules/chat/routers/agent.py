from fastapi import APIRouter,status,Depends, HTTPException
from src.common.dependencies import get_current_user
from src.utils.response import CustomResponse as cr
from src.models import Conversation, Customer

router = APIRouter()


@router.get("/conversations")
async def get_conversations(user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    sql = f'select a.id,a.customer_id, b.name customer_name from org_conversation a left join org_customer b on a.customer_id = b.id where a.organization_id = {organizationId}'
    records = await Conversation.sql(sql)
    return cr.success(data=records)

@router.get("/conversations/{conversation_id}")
async def conversation_detail(conversation_id: int, user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    record = await Conversation.get(conversation_id)

    if not record or record.organization_id != organizationId:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation Not found"
        )

    customer = await Customer.get(record.customer_id)

    return cr.success(data={"conversation": record.to_json(), "customer": customer.to_json()})
