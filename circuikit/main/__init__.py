from multiprocessing import Queue
from multiprocessing import Process
import time
from functools import partial
import threading
import signal
import sys

from ..services import Service
from ..serial_monitor_interface import (
    SerialMonitorInterface,
)
from ..serial_monitor_interface.types import SerialMonitorOptions

import logging

logger = logging.getLogger(__name__)


def smi_task(
    serial_monitor_options: SerialMonitorOptions,
    smi_output_queue: Queue,
    smi_input_queue: Queue,
):
    def on_next_read(sample: dict):
        smi_output_queue.put(sample)

    smi = SerialMonitorInterface(
        on_next_read=on_next_read,
        messages_to_send_queue=smi_input_queue,
        options=serial_monitor_options,
    )
    # fan in - single producer
    smi.start()

    while True:
        # stay alive
        time.sleep(60)

    # send a signal that no further tasks are coming
    smi_output_queue.put(None)


def app_task(
    services: list[Service], smi_output_queue: Queue, stop_event: threading.Event
):
    while not stop_event.is_set():
        # get a task from the queue
        sample = smi_output_queue.get()
        # check for signal that we are done
        if sample is None:
            break
        # process
        logger.debug(f"Fanning out smi {sample=}")

        for sub in services:
            sub.on_new_read(new_read=sample)


class Circuikit:
    __slots__ = (
        "serial_monitor_options",
        "services",
        "smi_output_queue",
        "smi_input_queue",
        "stop_event",
        "smi_process",
        "app_thread",
    )

    def __init__(
        self,
        serial_monitor_options: SerialMonitorOptions,
        services: list[Service],
    ):
        self.smi_output_queue = Queue()
        self.smi_input_queue = Queue()

        self.serial_monitor_options = serial_monitor_options
        self.services = services

        self.smi_process = Process(
            target=partial(
                smi_task,
                serial_monitor_options=self.serial_monitor_options,
                smi_output_queue=self.smi_output_queue,
                smi_input_queue=self.smi_input_queue,
            ),
            daemon=True,
        )
        # app task will happen in seprate thread but not in seperate process so it won't involve pickling
        # thus, user will be more verstailt with it's services
        self.stop_event = threading.Event()
        self.app_thread = threading.Thread(
            target=partial(
                app_task,
                services=self.services,
                smi_output_queue=self.smi_output_queue,
                stop_event=self.stop_event,
            ),
            daemon=True,
        )

        # Graceful cleanup function
        def cleanup():
            try:
                logger.debug("Circuikit cleanup start")
                self.stop()
                logger.debug("Circuikit cleanup end")
            except Exception as e:
                logger.error(f"Circuikit cleanup error: {e}")
                raise e

        # atexit.register(cleanup)
        def sig_handler(sig, frame):
            logger.debug(f"Circuikit caught {sig=}")
            cleanup()
            sys.exit(0)

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

    def __destroy__(self):
        self.stop()

    def send_smi_input(self, message: str) -> None:
        self.smi_input_queue.put(message)

    def start(self, block=False) -> None:
        self.smi_process.start()
        self.app_thread.start()

        if block:
            self.app_thread.join()

    def stop(self) -> None:
        if self.smi_process.is_alive():
            self.smi_process.terminate()
        if not self.stop_event.is_set():
            self.stop_event.set()
        self.smi_output_queue.close()
        self.smi_input_queue.close()
