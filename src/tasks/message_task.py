import json
import time
from typing import Optional

from celery.schedules import crontab
from confluent_kafka import Consumer, Producer
from sqlmodel import Session

from src.config.celery import celery_app
from src.db.config import async_session
from src.config.settings import settings

# Import models from centralized location to avoid circular imports
from src.models import Conversation, Message


@celery_app.task
def save_messages(conversation_id: int, data: dict, user_id: Optional[int] = None):
    try:
        print(f"saving message in queue for conversation_id: {conversation_id}")

        # Debug: Check if there are any conversations in the database
        all_conversations = Conversation.get_all()
        print(f"Total conversations in database: {len(all_conversations)}")
        if all_conversations:
            print(f"Available conversation IDs: {[c.id for c in all_conversations]}")

        conversation = Conversation.get(conversation_id)

        if not conversation:
            print(f"Conversation with ID {conversation_id} not found")
            return

        customer_id = conversation.customer_id
        print(f"Found conversation: {conversation.id}, customer_id: {customer_id}")

        if user_id:
            customer_id = None

        # Kafka producer logic
        try:
            producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
            kafka_payload = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "message": data.get("message"),
            }
            producer.produce(
                settings.KAFKA_TOPIC, json.dumps(kafka_payload).encode("utf-8")
            )
            producer.flush()
            print("Message sent to Kafka successfully")
        except Exception as kafka_error:
            print(f"Kafka connection error: {kafka_error}")
            print(f"Trying to connect to: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            # For now, just log the error and continue
            # In production, you might want to store messages in a fallback queue
    except Exception as e:
        print(f"kafka error producer {e}")
        import traceback

        traceback.print_exc()


@celery_app.task
def run_kafka_consumer_batch(
    batch_size: int = 20,
    poll_timeout: float = 1.0,
    flush_interval: float = 5.0,
    max_runtime: int = 30,  # Maximum runtime in seconds
):
    """
    Celery task to run a Kafka consumer that batches messages and bulk inserts them into the database.
    :param batch_size: Number of messages per batch insert
    :param poll_timeout: Kafka poll timeout in seconds
    :param flush_interval: Max seconds to wait before flushing batch
    :param max_runtime: Maximum runtime in seconds before stopping
    """
    print(
        f"[KAFKA CONSUMER] Starting run_kafka_consumer_batch - batch_size: {batch_size}, poll_timeout: {poll_timeout}, flush_interval: {flush_interval}, max_runtime: {max_runtime}"
    )
    print(
        f"[KAFKA CONSUMER] Kafka bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}"
    )
    print(f"[KAFKA CONSUMER] Kafka topic: {settings.KAFKA_TOPIC}")

    try:
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "chatboq-message-batch-consumer",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )
        print(f"[KAFKA CONSUMER] Kafka consumer created successfully")

        consumer.subscribe([settings.KAFKA_TOPIC])
        print(f"[KAFKA CONSUMER] Subscribed to topic: {settings.KAFKA_TOPIC}")
    except Exception as e:
        print(f"[KAFKA CONSUMER] Error creating Kafka consumer: {e}")
        return

    batch = []
    last_flush = time.time()
    start_time = time.time()
    print(f"[KAFKA CONSUMER] Kafka batch consumer started...")

    try:
        while True:
            # Check if we've exceeded max runtime
            if time.time() - start_time > max_runtime:
                print(
                    f"[KAFKA CONSUMER] Max runtime ({max_runtime}s) reached, stopping..."
                )
                break

            msg = consumer.poll(poll_timeout)
            print(f"[KAFKA CONSUMER] messages {msg}")
            now = time.time()

            if msg is not None and not msg.error():
                data = json.loads(msg.value().decode("utf-8"))
                batch.append(data)
                print(f"[KAFKA CONSUMER] Added message to batch: {data}")

            # Flush if batch size or interval reached
            if len(batch) >= batch_size or (
                batch and now - last_flush >= flush_interval
            ):
                print(f"[KAFKA CONSUMER] Flushing batch of {len(batch)} messages...")
                try:
                    # with Session(engine) as session:
                    #     objs = [
                    #         Message(
                    #             conversation_id=m['conversation_id'],
                    #             content=m['message'],
                    #             customer_id=None,  # Set if available in payload
                    #             user_id=m.get('user_id')
                    #         ) for m in batch
                    #     ]
                    #     session.add_all(objs)
                    #     session.commit()
                    print(
                        f"[KAFKA CONSUMER] Successfully inserted batch of {len(batch)} messages."
                    )
                except Exception as e:
                    print(
                        f"[KAFKA CONSUMER] Error inserting messages into database: {e}"
                    )
                    import traceback

                    traceback.print_exc()

                batch.clear()
                last_flush = now

    except Exception as e:
        print(f"[KAFKA CONSUMER] Error during consumer loop: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Flush any remaining messages
        if batch:
            print(f"[KAFKA CONSUMER] Flushing final batch of {len(batch)} messages...")
            try:
                with Session(engine) as session:
                    objs = [
                        Message(
                            conversation_id=m["conversation_id"],
                            content=m["message"],
                            customer_id=None,
                            user_id=m.get("user_id"),
                        )
                        for m in batch
                    ]
                    session.add_all(objs)
                    session.commit()
                print(
                    f"[KAFKA CONSUMER] Successfully inserted final batch of {len(batch)} messages."
                )
            except Exception as e:
                print(f"[KAFKA CONSUMER] Error inserting final batch: {e}")

        try:
            consumer.close()
            print(f"[KAFKA CONSUMER] Kafka consumer closed successfully")
        except Exception as e:
            print(f"[KAFKA CONSUMER] Error closing consumer: {e}")
        print(f"[KAFKA CONSUMER] Task completed")


# Periodic task is now configured in celery.py using beat_schedule


@celery_app.task
def check_kafka_messages():
    """
    Simple task that runs every 10 seconds to check for Kafka messages and save them to database.
    """
    print(f"[CHECK KAFKA] Starting check_kafka_messages task...")

    try:
        # Create Kafka consumer
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "chatboq-message-checker",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )

        consumer.subscribe([settings.KAFKA_TOPIC])
        print(f"[CHECK KAFKA] Subscribed to topic: {settings.KAFKA_TOPIC}")

        # Poll for messages (quick check)
        messages_found = 0
        for _ in range(5):  # Poll 5 times quickly
            msg = consumer.poll(0.5)  # 0.5 second timeout
            if msg is not None and not msg.error():
                data = json.loads(msg.value().decode("utf-8"))
                print(f"[CHECK KAFKA] Found message: {data}")

                # Save message to database immediately
                try:
                    with Session(engine) as session:
                        message = Message(
                            conversation_id=data["conversation_id"],
                            content=data["message"],
                            customer_id=None,
                            user_id=data.get("user_id"),
                        )
                        session.add(message)
                        session.commit()
                    print(f"[CHECK KAFKA] Saved message to database")
                    messages_found += 1
                except Exception as e:
                    print(f"[CHECK KAFKA] Error saving message: {e}")

        print(
            f"[CHECK KAFKA] Task completed. Found and saved {messages_found} messages."
        )

    except Exception as e:
        print(f"[CHECK KAFKA] Error in check_kafka_messages: {e}")
        import traceback

        traceback.print_exc()
    finally:
        try:
            consumer.close()
        except:
            pass


@celery_app.task
def consume_kafka_messages_batch(
    batch_size: int = 20, poll_timeout: float = 1.0, max_polls: int = 10
):
    """
    Celery task to consume a batch of messages from Kafka and insert them into the DB.
    :param batch_size: Number of messages per DB insert
    :param poll_timeout: Kafka poll timeout in seconds
    :param max_polls: How many times to poll Kafka per run
    """
    print(
        f"[PERIODIC TASK] Starting consume_kafka_messages_batch - batch_size: {batch_size}, poll_timeout: {poll_timeout}, max_polls: {max_polls}"
    )
    print(
        f"[PERIODIC TASK] Kafka bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}"
    )
    print(f"[PERIODIC TASK] Kafka topic: {settings.KAFKA_TOPIC}")

    try:
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "chatboq-message-batch-consumer",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )
        print(f"[PERIODIC TASK] Kafka consumer created successfully")

        consumer.subscribe([settings.KAFKA_TOPIC])
        print(f"[PERIODIC TASK] Subscribed to topic: {settings.KAFKA_TOPIC}")
    except Exception as e:
        print(f"[PERIODIC TASK] Error creating Kafka consumer: {e}")
        return

    batch = []
    try:
        print(f"[PERIODIC TASK] Starting to poll Kafka for messages...")
        for poll_count in range(max_polls):
            try:
                msg = consumer.poll(poll_timeout)
                print(
                    f"[PERIODIC TASK] Poll {poll_count + 1}/{max_polls}: Got message: {msg}"
                )
                if msg is not None and not msg.error():
                    data = json.loads(msg.value().decode("utf-8"))
                    batch.append(data)
                    print(f"[PERIODIC TASK] Added message to batch: {data}")
                elif msg is not None and msg.error():
                    print(f"[PERIODIC TASK] Message error: {msg.error()}")
                if len(batch) >= batch_size:
                    print(
                        f"[PERIODIC TASK] Batch size reached ({len(batch)}), stopping polls"
                    )
                    break
            except Exception as e:
                print(f"[PERIODIC TASK] Error during polling: {e}")
                break

        print(f"[PERIODIC TASK] Finished polling. Batch size: {len(batch)}")
        if batch:
            print(f"[PERIODIC TASK] Inserting {len(batch)} messages into database...")
            try:
                with Session(engine) as session:
                    objs = [
                        Message(
                            conversation_id=m["conversation_id"],
                            content=m["message"],
                            customer_id=None,  # Set if available in payload
                            user_id=m.get("user_id"),
                        )
                        for m in batch
                    ]
                    session.add_all(objs)
                    session.commit()
                print(
                    f"[PERIODIC TASK] Successfully inserted batch of {len(batch)} messages from Kafka."
                )
            except Exception as e:
                print(f"[PERIODIC TASK] Error inserting messages into database: {e}")
                import traceback

                traceback.print_exc()
        else:
            print(f"[PERIODIC TASK] No messages in batch to insert.")
    finally:
        try:
            consumer.close()
            print(f"[PERIODIC TASK] Kafka consumer closed successfully")
        except Exception as e:
            print(f"[PERIODIC TASK] Error closing consumer: {e}")
        print(f"[PERIODIC TASK] Task completed")
