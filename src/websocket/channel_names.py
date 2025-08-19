

AGENT_NOTIFICATION_CHANNEL = "chat-agent-notification-channel"
MESSAGE_CHANNEL = "chat-message-channel"
TYPING_CHANNEL = "chat-typing-channel"
TYPING_STOP_CHANNEL = "chat-typing-stop-channel"
MESSAGE_SEEN_CHANNEL = "chat-message-seen-channel"
CUSTOMER_NOTIFICATION_CHANNEL = "chat-customer-notification-channel"









def is_chat_channel(channel_name):
    return channel_name.startswith("chat-")
    