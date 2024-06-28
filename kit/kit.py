from multiprocessing import JoinableQueue
from multiprocessing import Process
import time
from .services import Service
from typing import Any
from functools import partial

from .serial_monitor_interface import (
    SerialMonitorInterface,
    ConcreteSerialMonitorInterface,
)


def smi_task(
    serial_monitor_interface: ConcreteSerialMonitorInterface,
    sample_rate_ms: float,
    readings_queue: JoinableQueue,
    writings_queue: JoinableQueue,
):
    def on_next_read(sample: Any):  # actually a dict...
        readings_queue.put(sample)

    smi = SerialMonitorInterface(
        on_next_read=on_next_read,
        messages_to_send_queue=writings_queue,
        concrete_interface=serial_monitor_interface,
        sample_rate_ms=sample_rate_ms,
    )
    # fan in - single producer
    smi.start()

    while True:
        # stay alive
        time.sleep(60)

    # send a signal that no further tasks are coming
    readings_queue.put(None)


def app_task(
    sub_services: list[Service],
    readings_queue: JoinableQueue,
    writings_queue: JoinableQueue,
):
    # process items from the queue
    def write_message_fn(message: str) -> None:
        writings_queue.put(message)

    # Set reply smi fn to already created subscribers
    for sub in sub_services:
        sub.set_reply_smi_fn(reply_smi_fn=write_message_fn)
    # call each srv start method
    for sub in sub_services:
        sub.start()

    while True:
        # get a task from the queue
        sample = readings_queue.get()
        # check for signal that we are done
        if sample is None:
            break
        # process
        print(f"Fanning out new_read={sample}", flush=True)

        for sub in sub_services:
            sub.on_new_read(new_read=sample)

        # mark the unit of work as processed
        readings_queue.task_done()

    # mark the signal as processed
    readings_queue.task_done()


class Kit:
    __slots__ = (
        "serial_monitor_interface",
        "sample_rate_ms",
        "sub_services",
        "readings_queue",
        "writings_queue",
        "smi_process",
        "app_process",
    )

    def __init__(
        self,
        serial_monitor_interface: ConcreteSerialMonitorInterface,
        sample_rate_ms: float,
        sub_services: list[Service],
    ):
        self.readings_queue = JoinableQueue()
        self.writings_queue = JoinableQueue()

        self.serial_monitor_interface = serial_monitor_interface
        self.sample_rate_ms = sample_rate_ms
        self.sub_services = sub_services

        self.smi_process = Process(
            target=partial(
                smi_task,
                serial_monitor_interface=self.serial_monitor_interface,
                sample_rate_ms=self.sample_rate_ms,
                readings_queue=self.readings_queue,
                writings_queue=self.writings_queue,
            ),
            daemon=True,
        )

        self.app_process = Process(
            target=partial(
                app_task,
                sub_services=self.sub_services,
                readings_queue=self.readings_queue,
                writings_queue=self.writings_queue,
            ),
            daemon=True,
        )

    def __destroy__(self):
        self.stop()

    def start(self) -> None:
        self.smi_process.start()
        self.app_process.start()

        self.app_process.join()

        self.readings_queue.join()
        self.writings_queue.join()

    def stop(self) -> None:
        if self.smi_process.is_alive():
            self.smi_process.terminate()
        if self.app_process.is_alive():
            self.app_process.terminate()
        self.readings_queue.close()
        self.writings_queue.close()
