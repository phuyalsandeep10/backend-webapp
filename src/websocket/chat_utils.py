from src.models import Message, MessageAttachment, Conversation


class ChatUtils:
    @staticmethod
    def customer_notification_group(org_id: int):
        return f"org-{org_id}-customers"

    @staticmethod
    def user_notification_group(org_id: int):
        return f"org-{org_id}-users"
    
    @staticmethod
    def _user_add_sid(userId:int):
        return f"ws:user:sid:{userId}"

    @staticmethod
    def conversation_group(conversation_id: int):
        return f"conversation-{conversation_id}"

    @staticmethod
    def user_conversation_group(conversation_id: int):
        return f"users-conversation-{conversation_id}"

    @staticmethod
    def get_room_channel(conversation_id: int) -> str:
        return f"conversation-{conversation_id}"

    @staticmethod
    async def save_message_seen(conversation_id: int, message_id: str):
        message = await Message.find_one(where={"message_id": message_id})
        if not message:
            return False
        await Conversation.update(
            id=conversation_id, attributes={"last_message": message.to_json()}
        )

    @staticmethod
    async def join_conversation(conversation_id: int, user_id: str):
        print(f"join conversation in db and user_id {user_id}")
        conversation_id = int(conversation_id)

        conversation_member = await ConversationMember.find_one({
            "conversation_id": conversation_id,
            "user_id": user_id
        })
        

        if not conversation_member:
            await ConversationMember.create(
                conversation_id=conversation_id,
                user_id=user_id
            )
        

    @staticmethod
    async def save_message_db(conversation_id: int, payload: dict):
        print(f"save message in db and payload {payload}")
        conversation_id = int(conversation_id)

        data = {}
        data["content"] = payload.get("message")
        data["message_id"] = payload.get("message_id")
        data["conversation_id"] = conversation_id
        if payload.get("customer_id"):
            data["customer_id"] = payload.get("customer_id")
        if payload.get("user_id"):
            data["user_id"] = payload.get("user_id")

        if payload.get("reply_id"):
            data["reply_id"] = payload.get("reply_id")
        if payload.get("organization_id"):
            data["organization_id"] = payload.get("organization_id")

        msg = await Message.create(**data)

        for file in payload.get("files", []):
            await MessageAttachment.create(
                message_id=msg.id,
                file_url=file.get("url"),
                file_name=file.get("file_name"),
                file_type=file.get("file_type"),
                file_size=file.get("file_size"),
            )
        await ChatUtils.save_last_message(conversation_id, payload.get("message_id"))

        return msg
