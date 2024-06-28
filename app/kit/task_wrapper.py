from app.models import Sensors
from app.kit.task import Task
from typing import Callable


class TaskWrapper(Task):
    """Acts as a wrapper that transmit non-task superset the sensors as it was one"""

    def __init__(self, on_new_message_fn: Callable[[Sensors], None]):
        super().__init__()
        self.on_new_message_fn = on_new_message_fn

    def on_message(self, message: Sensors) -> None:
        self.on_new_message_fn(message)
