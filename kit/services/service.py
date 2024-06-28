import threading
import queue
from abc import ABC, abstractmethod


def default_reply_smi_fn(message: str) -> None:
    print(f"[DEFAULT REPLY SMI] print; msg={message}")


class Service(ABC):
    def __destroy__(self):
        if self.stop_event is not None:
            self.stop_event.set()

    @abstractmethod
    def on_message(self, message: dict) -> None:
        # Do your thing
        pass

    def start(self) -> None:
        # Starting everything related to threading in independent methond than form __init__ so class will be picklable
        self.messages_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(
            target=self.pull_requests,
            daemon=True,
        )
        self.worker_thread.start()

    def on_new_read(self, new_read: dict) -> None:
        self.messages_queue.put(new_read)

    def pull_requests(self):
        while not self.stop_event.is_set():
            message = self.messages_queue.get()
            if message is not None:
                self.on_message(message=message)
                self.messages_queue.task_done()
