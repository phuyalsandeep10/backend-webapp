from abc import abstractmethod
from typing import Any

from src.factory.notification.email_notification import EmailNotification


class NotificationFactory:

    @staticmethod
    def create(name: str) -> Any:
        if name == "email":
            return EmailNotification()
        else:
            raise ValueError("value error in notifaction factory")
