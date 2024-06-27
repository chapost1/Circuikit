from .radar import Radar
from .mac_os_sms_sender import send_sms
from .notification_channel import NotificationChannel
from .alert_manager import AlertManager
from .logger import ReadingsLogger
from .thingsboard_gateway import ThingsBoardGateway
from .controller import Controller
from typing import Protocol, Callable
from functools import partial
from .models import Sensors

from dirty.env import (
    SMS_DESTINATION_PHONE_NUMBER,
    READINGS_LOG_FILE_PATH,
    THINGSBOARD_TOKEN,
)


class NewReadObservers(Protocol):
    def on_new_read(self, new_read: Sensors):
        pass


class AppInterface:
    __slots__ = ("write_message_fn", "subscribers")

    def __init__(self, write_message_fn: Callable[[str], None]):
        self.write_message_fn = write_message_fn

        self.subscribers: list[NewReadObservers] = [
            ThingsBoardGateway(token=THINGSBOARD_TOKEN),
            Controller(write_message_fn=write_message_fn),
            Radar(),
            AlertManager(
                notification_channel=NotificationChannel(
                    notify_fn=partial(
                        send_sms, phone_number=SMS_DESTINATION_PHONE_NUMBER
                    )
                )
            ),
            ReadingsLogger(file_path=READINGS_LOG_FILE_PATH, flush_treshold=60),
        ]

    def _fan_out(self, sample: dict):
        read = Sensors(**sample)
        for sub in self.subscribers:
            sub.on_new_read(new_read=read)

    def on_new_read(self, sample: dict):
        self._fan_out(sample=sample)
