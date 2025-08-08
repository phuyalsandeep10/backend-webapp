from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Contains all the environment variables
    """

    # def __init__(self):
    #     super()

    celery_broker_url: str = "redis://localhost:6379"
    PROJECT_NAME: str = "Chatboq Service"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Chatboq Service API"
    DATABASE_URL: str = ""
    ASYNC_DATABASE_URL: str = ""
    API_PREFIX: str = "/api/v1"
    CELEREY_BROKER_URL: str = "redis://localhost:6379"

    # ALLOWED_HOSTS: List[str] = ["*"]
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token expiration time in minutes
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"
    KAFKA_TOPIC: str = "chatboq-events"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "chatboq_db"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"

    APPLE_CLIENT_ID: str = "your-apple-client-id"
    APPLE_CLIENT_SECRET: str = "your-apple-client-secret"

    FRONTEND_URL: str = ""
    CELEREY_BROKER_URL: str = "redis://localhost:6379"

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type:ignore
