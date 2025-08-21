from abc import abstractmethod


class NotificationInterface:
    @abstractmethod
    def send(self):
        pass
