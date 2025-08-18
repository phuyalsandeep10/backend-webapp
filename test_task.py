#!/usr/bin/env python3
import asyncio
import redis.asyncio as redis
from src.config.settings import settings

async def simple_redis_listener():
    """Simplified version of redis_listener for testing"""
    print("🚀 Simple Redis listener started")
    
    redis_client = None
    pubsub = None
    
    try:
        print("🔌 Connecting to Redis...")
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = redis_client.pubsub()
        
        print("📡 Subscribing to pattern '*'...")
        await pubsub.psubscribe("*")
        print("✅ Subscribed successfully")
        
        # Keep the subscription alive for 10 seconds
        print("⏰ Keeping subscription alive for 10 seconds...")
        await asyncio.sleep(10)
        print("⏰ 10 seconds completed")
        
    except Exception as e:
        print(f"❌ Error in simple listener: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if pubsub:
            await pubsub.aclose()
        if redis_client:
            await redis_client.aclose()
        print("🧹 Cleanup completed")

async def test_task_management():
    """Test task creation and management"""
    print("🧪 Testing task management...")
    
    # Create task with error handling
    task = asyncio.create_task(simple_redis_listener())
    
    def task_done_callback(t):
        if t.exception():
            print(f"❌ Task failed: {t.exception()}")
        else:
            print("✅ Task completed successfully")
    
    task.add_done_callback(task_done_callback)
    
    # Wait a bit, then check Redis
    await asyncio.sleep(2)
    
    # Check if subscription is active
    check_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        # Publish a test message
        result = await check_client.publish("test_channel", "hello")
        print(f"📡 Published test message, {result} subscribers received it")
    finally:
        await check_client.aclose()
    
    # Wait for task to complete
    await task
    print("🏁 Test completed")

if __name__ == "__main__":
    asyncio.run(test_task_management())
