PROJECT_NAME = "MyProject"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "This is a sample project to demonstrate configuration settings."
DATABASE_URL = "sqlite:///./test.db"
API_PREFIX = "/api"
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "your-secret-key"

import os

# Use 'kafka:9092' if running in Docker, else 'localhost:29092'
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "kafka:9092" if os.getenv("IN_DOCKER") else "localhost:29092",
)
KAFKA_TOPIC = "chat-messages"


class settings:
    PROJECT_NAME: str = PROJECT_NAME
    PROJECT_VERSION: str = PROJECT_VERSION
    PROJECT_DESCRIPTION: str = PROJECT_DESCRIPTION
    DATABASE_URL: str = DATABASE_URL
    API_PREFIX: str = API_PREFIX
    ALLOWED_HOSTS: list[str] = ALLOWED_HOSTS
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    KAFKA_BOOTSTRAP_SERVERS: str = KAFKA_BOOTSTRAP_SERVERS
    KAFKA_TOPIC: str = KAFKA_TOPIC
