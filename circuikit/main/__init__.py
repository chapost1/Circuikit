from multiprocessing import Queue
from multiprocessing import Process
import time
from functools import partial

from ..serial_monitor_interface import (
    SerialMonitorInterface,
)
from ..serial_monitor_interface.types import SerialMonitorOptions, Sample

from ..protocols import AllocateServicesFn


def smi_task(
    serial_monitor_options: SerialMonitorOptions,
    smi_output_queue: Queue,
    smi_input_queue: Queue,
):
    def on_next_read(sample: Sample):
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
    allocate_services_fn: AllocateServicesFn,
    smi_output_queue: Queue,
    smi_input_queue: Queue,
):
    # process items from the queue
    def write_message_fn(message: str) -> None:
        smi_input_queue.put(message)

    sub_services = allocate_services_fn(send_smi_input=write_message_fn)

    # call each srv start method
    for sub in sub_services:
        sub.start()

    while True:
        # get a task from the queue
        sample = smi_output_queue.get()
        # check for signal that we are done
        if sample is None:
            break
        # process
        print(f"Fanning out new_read={sample}", flush=True)

        for sub in sub_services:
            sub.on_new_read(new_read=sample)


class Circuikit:
    __slots__ = (
        "serial_monitor_options",
        "allocate_services_fn",
        "smi_output_queue",
        "smi_input_queue",
        "smi_process",
        "app_process",
    )

    def __init__(
        self,
        serial_monitor_options: SerialMonitorOptions,
        allocate_services_fn: AllocateServicesFn,
    ):
        self.smi_output_queue = Queue()
        self.smi_input_queue = Queue()

        self.serial_monitor_options = serial_monitor_options
        self.allocate_services_fn = allocate_services_fn

        self.smi_process = Process(
            target=partial(
                smi_task,
                serial_monitor_options=self.serial_monitor_options,
                smi_output_queue=self.smi_output_queue,
                smi_input_queue=self.smi_input_queue,
            ),
            daemon=True,
        )

        self.app_process = Process(
            target=partial(
                app_task,
                allocate_services_fn=self.allocate_services_fn,
                smi_output_queue=self.smi_output_queue,
                smi_input_queue=self.smi_input_queue,
            ),
            daemon=True,
        )

    def __destroy__(self):
        self.stop()

    def start(self) -> None:
        self.smi_process.start()
        self.app_process.start()

        self.app_process.join()

    def stop(self) -> None:
        if self.smi_process.is_alive():
            self.smi_process.terminate()
        if self.app_process.is_alive():
            self.app_process.terminate()
        self.smi_output_queue.close()
        self.smi_input_queue.close()
