import json
from typing import Callable, TypedDict, Protocol
import time
import threading
import queue

MIN_SAMPLE_RATE_MS = 25


class ConcreteSerialMonitorInterface(Protocol):
    def send_message(self, message: str) -> None:
        pass

    def sample(self) -> str | None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class QueueProtocol(Protocol):
    def get(self):
        pass

    def put(self, obj, block: bool = True, timeout: float | None = None) -> None:
        pass

    def task_done(self) -> None:
        pass


class Sample(TypedDict):
    time: int
    ...


def sample_serial_monitor(
    on_new_read: Callable[[list[Sample]], None],
    sample_rate_ms: float,
    stop_event: threading.Event,
    sample_fn: Callable[[], str | None],
):
    # so basically serial monitor is bound to max line of 60
    # so reading all of it all the time and take last should be fine as long as
    # the service output in less frequent than the python read rate
    while not stop_event.is_set():
        text = sample_fn()
        if text is None:
            print("serial monitor text is None")
            continue
        samples = extract_valid_samples(text)
        on_new_read(samples)
        time.sleep(sample_rate_ms / 1000)


def extract_valid_samples(data: str):
    samples: list[Sample] = []
    lines = data.split("\n")
    for line in lines:
        try:
            sample: Sample = json.loads(line)
            if not isinstance(sample, dict):
                continue
            if not "time" in sample:
                print(f"sample={sample} has no .time key, skipping...")
                continue
            samples.append(sample)
        except ValueError:
            # print(f'faled to load incomplete line={line}')
            # that's expected...
            pass
    return samples


def watch(
    on_next_read: Callable[[Sample], None],
    stop_event: threading.Event,
    sample_rate_ms: float,
    sample_fn: Callable[[], str | None],
):
    last_sample_time = -1

    def on_new_read(new_samples: list[Sample]):
        nonlocal last_sample_time
        delta_samples: list[Sample] = []
        if len(new_samples) == 0:
            return
        for sample in new_samples:
            if sample["time"] > last_sample_time:
                delta_samples.append(sample)

        last_sample_time = new_samples[-1]["time"]

        for sample in delta_samples:
            on_next_read(sample)

    sample_serial_monitor(
        on_new_read=on_new_read,
        stop_event=stop_event,
        sample_fn=sample_fn,
        sample_rate_ms=sample_rate_ms,
    )


def speak_with_serial_monitor(
    messages_queue: QueueProtocol,
    stop_event: threading.Event,
    send_message_fn: Callable[[str], None],
):
    while not stop_event.is_set():
        message = messages_queue.get()
        if message is None:
            print("[speak_with_serial_monitor] message is none")
            continue
        send_message_fn(message)
        messages_queue.task_done()


class SerialMonitorInterface:
    __slots__ = (
        "sample_rate_ms",
        "concrete_interface",
        "messages_to_send_queue",
        "sender_thread",
        "watcher_thread",
        "stop_event",
    )

    def __init__(
        self,
        concrete_interface: ConcreteSerialMonitorInterface,
        sample_rate_ms: float,
        on_next_read: Callable[[Sample], None],
        messages_to_send_queue: QueueProtocol = queue.Queue(),  # type: ignore
    ):
        # validators
        if sample_rate_ms < MIN_SAMPLE_RATE_MS:
            raise ValueError(f"Minimum sample_rate_ms value is {MIN_SAMPLE_RATE_MS}")

        self.messages_to_send_queue = messages_to_send_queue

        self.stop_event = threading.Event()

        self.concrete_interface = concrete_interface

        self.sample_rate_ms = sample_rate_ms

        self.sender_thread = threading.Thread(
            target=speak_with_serial_monitor,
            args=(
                self.messages_to_send_queue,
                self.stop_event,
                self.concrete_interface.send_message,
            ),
            daemon=True,
        )
        self.watcher_thread = threading.Thread(
            target=watch,
            args=(
                on_next_read,
                self.stop_event,
                self.sample_rate_ms,
                self.concrete_interface.sample,
            ),
            daemon=True,
        )

    def __destroy__(self):
        self.stop()

    def send_message(self, message: str) -> None:
        self.messages_to_send_queue.put(message)

    def start(self) -> None:
        self.concrete_interface.start()
        self.sender_thread.start()
        self.watcher_thread.start()

    def stop(self) -> None:
        if self.sender_thread.is_alive():
            self.stop_event.set()
        self.concrete_interface.stop()
