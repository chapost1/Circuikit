from .models import Sensors
import threading
import queue
from abc import ABC, abstractmethod


class Task(ABC):
    def __init__(self):
        self.messages_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(
            target=self.pull_requests,
            daemon=True,
        )
        self.worker_thread.start()

    def __destroy__(self):
        self.stop_event.set()

    @abstractmethod
    def on_message(self, message: Sensors) -> None:
        # Do your thing
        pass

    def on_new_read(self, new_read: Sensors) -> None:
        self.messages_queue.put(new_read)

    def pull_requests(self):
        while not self.stop_event.is_set():
            message = self.messages_queue.get()
            if message is not None:
                self.on_message(message=message)
                self.messages_queue.task_done()
