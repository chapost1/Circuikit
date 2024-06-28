from app.kit import Task, TaskWrapper, ThingsBoardGateway, FileLogger
from typing import Callable
from app.models import Sensors
from app.example_gui import ExampleGUI

from dirty.env import (
    THINGSBOARD_TOKEN,
)


class AppInterface:
    __slots__ = ("write_message_fn", "subscribers")

    def __init__(self, write_message_fn: Callable[[str], None]):
        self.write_message_fn = write_message_fn
        # If you want any app task to send message to the serial monitor
        # Then, just pass it as a DI the self.write_message_fn
        # And call it whenever you want to send data to it

        ex_gui = ExampleGUI()
        ex_gui_task = TaskWrapper(on_new_message_fn=ex_gui.update_screen)

        self.subscribers: list[Task] = [
            ThingsBoardGateway(token=THINGSBOARD_TOKEN),
            ex_gui_task,
            FileLogger(),
        ]

    def _fan_out(self, sample: dict):
        read = Sensors(**sample)
        print(f"Fanning out new_read={sample}", flush=True)
        for sub in self.subscribers:
            sub.on_new_read(new_read=read)

    def on_new_read(self, sample: dict):
        self._fan_out(sample=sample)  #
