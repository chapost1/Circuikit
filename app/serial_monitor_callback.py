from app.models import Sensors
from app.task import Task
from typing import Callable


class SerialMonitorCallback(Task):
    def __init__(self, write_message_fn: Callable[[str], None]):
        super().__init__()
        self.write_message_fn = write_message_fn

    def on_message(self, message: Sensors) -> None:
        # Write your logic, you can add another thread and do something in loop
        # Or you can just listen to certain message content and act)
        pass

    def send_message(self, message: str) -> None:
        # Call it whenever you want from any other app task
        self.write_message_fn(message)
