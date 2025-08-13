

def customer_notification_group(org_id: int):
    return f"org-{org_id}-customers"


def user_notification_group(org_id: int):
    return f"org-{org_id}-users"


def conversation_group(conversationId: int):
    return f"conversation-{conversationId}"

def get_room_channel(conversation_id: int) -> str:
    print(f"get_room_channel called with conversation_id: {conversation_id}")
    return f"conversation-{conversation_id}"