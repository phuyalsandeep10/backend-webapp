AGENT_NOTIFICATION_CHANNEL = "chat-agent-notification-channel"
MESSAGE_CHANNEL = "chat-message-channel"
TYPING_CHANNEL = "chat-typing-channel"
TYPING_STOP_CHANNEL = "chat-typing-stop-channel"
MESSAGE_SEEN_CHANNEL = "chat-message-seen-channel"
CUSTOMER_NOTIFICATION_CHANNEL = "chat-customer-notification-channel"
AGENT_JOIN_CONVERSATION_CHANNEL = "chat-agent-join-conversation-channel"
AGENT_AVAILABILITY_CHANNEL = "chat-agent-availability-channel"

CONVERSATION_UNRESOLVED_CHANNEL = "chat-conversation-unresolved-channel"

def is_chat_channel(channel_name):
    return channel_name.startswith("chat-")
