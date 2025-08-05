from src.models import Customer,Conversation, Organization



async def create_customer_seed():
    customer = {
        'ip_address':'203.0.113.1',
        'email':'customer@chatboq.com',
        'phone':'1234567890',
        'name':'Guest-1',
    }
    org = await Organization.first()
    if not org:
        print("Organization not found")
        return
    customer['organization_id'] = org.id
    customer = await Customer.create(**customer)
    print("Customer created")

    conversation = {
        'ip_address':'203.0.113.1',
        'customer_id':customer.id,
        'organization_id':org.id,
    }
    conversation = await Conversation.create(**conversation)
    print("Conversation created")
    
