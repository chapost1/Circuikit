from .models import Sensors
from typing import Protocol


class NotificationChannel(Protocol):
    def notify(self, message: str) -> None:
        pass


class AlertManager:
    __slots__ = "notification_channel"

    def __init__(self, notification_channel: NotificationChannel):
        self.notification_channel = notification_channel

    def on_new_read(self, new_read: Sensors):
        print(f"[AL]: {new_read}", flush=True)
