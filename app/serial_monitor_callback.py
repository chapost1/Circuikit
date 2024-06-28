from app.models import Sensors
from app.task import Task
from typing import Callable


class SerialMonitorCallback(Task):
    __slots__ = "write_message_fn", "worker_thread", "messages_queue", "stop_event"

    def __init__(self, write_message_fn: Callable[[str], None]):
        super().__init__()
        self.write_message_fn = write_message_fn

    def on_message(self, message: Sensors):
        # Write your logic, you can add another thread and do something in loop
        # Or you can just listen to certain message content and act
        self.write_message_fn("Hello World")
        pass
