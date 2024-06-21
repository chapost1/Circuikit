from multiprocessing import JoinableQueue
from multiprocessing import Process
import serial_monitor_watcher
import radar
import alert_manager

# import logger
from typing import Any, Protocol
from models import UltrasonicRead


class NewReadObservers(Protocol):
    def on_new_read(self, new_read: UltrasonicRead):
        pass


subscribers: list[NewReadObservers] = [
    radar,
    alert_manager,
    # logger.ReadingsLogger()
]


def fan_out(sample: dict):
    read = UltrasonicRead(**sample)
    for sub in subscribers:
        sub.on_new_read(new_read=read)


# task for the producer process
def producer(queue: JoinableQueue):
    print("Producer starting", flush=True)

    def on_next_read(sample: Any):  # actually a dict...
        queue.put(sample)

    # fan in - single producer
    serial_monitor_watcher.watch(on_next_read=on_next_read)
    # send a signal that no further tasks are coming
    queue.put(None)
    print("Producer finished", flush=True)


# task for the consumer process
def consumer(queue: JoinableQueue):
    print("Consumer starting", flush=True)
    # process items from the queue
    while True:
        # get a task from the queue
        sample = queue.get()
        # check for signal that we are done
        if sample is None:
            break
        # process
        fan_out(sample=sample)
        # mark the unit of work as processed
        queue.task_done()

    # mark the signal as processed
    queue.task_done()
    print("Consumer finished", flush=True)


# entry point
if __name__ == "__main__":
    # create the shared queue
    queue = JoinableQueue()
    # create and start the producer process
    producer_process = Process(target=producer, args=(queue,), daemon=True)
    producer_process.start()
    # create and start the consumer process
    consumer_process = Process(target=consumer, args=(queue,), daemon=True)
    consumer_process.start()
    # wait for the producer to finish
    producer_process.join()
    print("Main found that the producer has finished", flush=True)
    # wait for the queue to empty
    queue.join()
    print("Main found that all tasks are processed", flush=True)
