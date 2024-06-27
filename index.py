from multiprocessing import JoinableQueue
from multiprocessing import Process
import time
from typing import Any

import serial_monitor_interface
import app

from dirty.env import (
    SELENIUM_THINKERCAD_URL,
    SELENIUM_DEBUGGER_PORT,
)


def smi_task(readins_queue: JoinableQueue, writings_queue: JoinableQueue):
    def on_next_read(sample: Any):  # actually a dict...
        readins_queue.put(sample)

    selenium_interface = serial_monitor_interface.SeleniumInterface(
        thinkercad_url=SELENIUM_THINKERCAD_URL, debugger_port=SELENIUM_DEBUGGER_PORT
    )

    smi = serial_monitor_interface.SerialMonitorInterface(
        on_next_read=on_next_read,
        messages_to_send_queue=writings_queue,
        concrete_interface=selenium_interface,
    )
    # fan in - single producer
    smi.start()

    while True:
        # stay alive
        time.sleep(60)

    # send a signal that no further tasks are coming
    readins_queue.put(None)


def app_task(readins_queue: JoinableQueue, writings_queue: JoinableQueue):
    # process items from the queue
    def write_message_fn(message: str):
        writings_queue.put(message)

    ai = app.AppInterface(write_message_fn=write_message_fn)

    while True:
        # get a task from the queue
        sample = readins_queue.get()
        # check for signal that we are done
        if sample is None:
            break
        # process

        ai.on_new_read(sample=sample)
        # mark the unit of work as processed
        readins_queue.task_done()

    # mark the signal as processed
    readins_queue.task_done()
    print("Consumer finished", flush=True)


# entry point
if __name__ == "__main__":
    readins_queue = JoinableQueue()
    writings_queue = JoinableQueue()

    smi_process = Process(
        target=smi_task,
        args=(
            readins_queue,
            writings_queue,
        ),
        daemon=True,
    )
    smi_process.start()

    app_process = Process(
        target=app_task,
        args=(
            readins_queue,
            writings_queue,
        ),
        daemon=True,
    )
    app_process.start()

    app_process.join()

    readins_queue.join()
    writings_queue.join()
    print("Main found that all tasks are processed", flush=True)
