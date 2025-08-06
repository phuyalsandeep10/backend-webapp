from src.models import Customer, Conversation, Organization, CustomerVisitLogs


async def create_customer_seed():
    print("Creating customer seed")
    customer = {
        "ip_address": "203.0.113.1",
        "email": "customer@chatboq.com",
        "phone": "1234567890",
        "name": "Guest-1",
    }
    org = await Organization.first()
    if not org:
        print("Organization not found")
        return
    customer["organization_id"] = org.id
    customer = await Customer.create(**customer)
    print("Customer created")

    conversation = {
        "ip_address": "203.0.113.1",
        "customer_id": customer.id,
        "organization_id": org.id,
    }
    conversation = await Conversation.create(**conversation)
    print("Conversation created")


async def create_customer_logs_seed():
    print("Creating customer logs seed")
    customer = await Customer.first()
    if not customer:
        print("Customer not found")
        return
    customer_logs = {
        "customer_id": customer.id,
        "ip_address": "203.0.113.1",
        "city": "New York",
        "country": "United States",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "device": "Chrome",
        "browser": "Chrome",
        "os": "Windows",
    }
    await CustomerVisitLogs.create(**customer_logs)
    print("Customer logs created")
