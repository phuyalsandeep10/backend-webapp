from sqlalchemy import event
from src.models import Message ,Conversation # your model
import asyncio


async def update_conversation_last_message(message):
    print("update_conversation_last_message ")
    await Conversation.update(message.conversation_id, attributes={"last_message": message.to_json()})


def do_async_task(func, *args, **kwargs):
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(func(*args, **kwargs))
    except Exception as e:
        print(f"Error updating conversation last message: {e}")
  

# Example: log when a user is created
@event.listens_for(Message, "after_insert")
def after_insert_message(mapper, connection, target):
    do_async_task(update_conversation_last_message, target)

    

# # Example: log when a user is updated
@event.listens_for(Message, "after_update")
def after_update_message(mapper, connection, target):
    do_async_task(update_conversation_last_message, target)
