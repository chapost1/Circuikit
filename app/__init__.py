from app.task import Task
from app.gui import GUI
from app.thingsboard_gateway import ThingsBoardGateway
from app.serial_monitor_callback import SerialMonitorCallback
from typing import Callable
from app.models import Sensors

from dirty.env import (
    THINGSBOARD_TOKEN,
)


class AppInterface:
    __slots__ = ("write_message_fn", "subscribers")

    def __init__(self, write_message_fn: Callable[[str], None]):
        self.write_message_fn = write_message_fn

        smc = SerialMonitorCallback(write_message_fn=write_message_fn)
        # If you want any other app task to send message to the serial monitor
        # Then, just add it's constructor some send fn param
        # and then do like: service(some_send_fn=smc.send_message)
        # and add logic in the service....

        self.subscribers: list[Task] = [
            smc,
            ThingsBoardGateway(token=THINGSBOARD_TOKEN),
            GUI(),
        ]

    def _fan_out(self, sample: dict):
        read = Sensors(**sample)
        print(f"Fanning out new_read={sample}", flush=True)
        for sub in self.subscribers:
            sub.on_new_read(new_read=read)

    def on_new_read(self, sample: dict):
        self._fan_out(sample=sample)
