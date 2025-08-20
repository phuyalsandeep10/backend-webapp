#!/usr/bin/env python3
import asyncio
import redis.asyncio as redis
from src.config.settings import settings


async def debug_redis_listener():
    print("🔍 DEBUG: Starting redis listener diagnostic...")

    redis_client = None
    pubsub = None

    try:
        print("🔍 DEBUG: Step 1 - Creating Redis client...")
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        print("✅ DEBUG: Redis client created")

        print("🔍 DEBUG: Step 2 - Testing basic connection...")
        pong = await redis_client.ping()
        print(f"✅ DEBUG: Redis ping successful: {pong}")

        print("🔍 DEBUG: Step 3 - Creating pubsub...")
        pubsub = redis_client.pubsub()
        print("✅ DEBUG: Pubsub created")

        print("🔍 DEBUG: Step 4 - Subscribing to pattern...")
        await pubsub.psubscribe("*")
        print("✅ DEBUG: Pattern subscription completed")

        print("🔍 DEBUG: Step 5 - Waiting for subscription to register...")
        await asyncio.sleep(0.5)
        print("✅ DEBUG: Wait completed")

        print("🔍 DEBUG: Step 6 - Testing with a message...")
        test_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            result = await test_client.publish("debug_test", "hello")
            print(f"✅ DEBUG: Published test message, {result} subscribers")
        finally:
            await test_client.aclose()

        print("🔍 DEBUG: Step 7 - Listening for messages (5 second timeout)...")
        message_count = 0
        try:
            async with asyncio.timeout(5.0):
                async for message in pubsub.listen():
                    message_count += 1
                    print(f"📨 DEBUG: Message {message_count}: {message}")
                    if message["type"] == "pmessage":
                        print("✅ DEBUG: Got pattern message - listener is working!")
                        break
                    if message_count > 10:  # Safety break
                        break
        except asyncio.TimeoutError:
            print("⏰ DEBUG: Timeout - no messages received")

    except Exception as e:
        print(f"❌ DEBUG: Error at step: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("🔍 DEBUG: Cleanup...")
        if pubsub:
            try:
                await pubsub.aclose()
                print("✅ DEBUG: Pubsub closed")
            except Exception as e:
                print(f"⚠️ DEBUG: Pubsub close error: {e}")

        if redis_client:
            try:
                await redis_client.aclose()
                print("✅ DEBUG: Redis client closed")
            except Exception as e:
                print(f"⚠️ DEBUG: Redis client close error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_redis_listener())
