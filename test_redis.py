#!/usr/bin/env python3
import asyncio
import redis.asyncio as redis


async def test_redis_pubsub():
    print("🧪 Testing Redis pub/sub connection...")

    # Test basic Redis connection
    try:
        client = redis.from_url("redis://localhost:6379", decode_responses=True)
        pong = await client.ping()
        print(f"✅ Redis ping: {pong}")
        await client.close()
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return

    # Test pub/sub
    subscriber = None
    publisher = None

    try:
        # Create subscriber
        subscriber = redis.from_url("redis://localhost:6379", decode_responses=True)
        pubsub = subscriber.pubsub()

        # Subscribe to pattern
        await pubsub.psubscribe("test_*")
        print("✅ Subscribed to pattern test_*")

        # Create publisher
        publisher = redis.from_url("redis://localhost:6379", decode_responses=True)

        # Give subscription time to register
        await asyncio.sleep(0.1)

        # Publish test message
        result = await publisher.publish("test_channel", "hello world")
        print(f"📡 Published message, {result} subscribers received it")

        # Listen for messages (with timeout)
        try:
            async with asyncio.timeout(2.0):
                async for message in pubsub.listen():
                    print(f"📨 Received: {message}")
                    if message["type"] == "pmessage":
                        print(
                            f"✅ Got pattern message: {message['data']} from {message['channel']}"
                        )
                        break
        except asyncio.TimeoutError:
            print("⏰ Timeout waiting for message")

    except Exception as e:
        print(f"❌ Pub/sub test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if subscriber:
            await subscriber.close()
        if publisher:
            await publisher.close()


if __name__ == "__main__":
    asyncio.run(test_redis_pubsub())
