import json
from typing import Callable
import time
import threading
from functools import partial
from .protocols import QueueProtocol
from .types import SerialMonitorOptions
import logging

logger = logging.getLogger(__name__)

MIN_SAMPLE_RATE_MS = 25


def sample_serial_monitor(
    on_new_read: Callable[[list[dict]], None],
    timestamp_field_name: str,
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
            logger.warning(
                "Sampled serial monitor output, but received None as a response"
            )
            continue
        samples = extract_valid_samples(
            data=text, timestamp_field_name=timestamp_field_name
        )
        on_new_read(samples)
        time.sleep(sample_rate_ms / 1000)


def extract_valid_samples(data: str, timestamp_field_name: str):
    samples: list[dict] = []
    lines = data.split("\n")
    for line in lines:
        try:
            sample: dict = json.loads(line)
            if not isinstance(sample, dict):
                continue
            if not timestamp_field_name in sample:
                logger.warning(
                    f"{sample=} has no {timestamp_field_name=} key, skipping..."
                )
                continue
            samples.append(sample)
        except ValueError:
            logger.debug(f"failed to load incomplete JSON {line=}")
            # that's expected in case of not a JSON or if sample taken during output is in progress...
            pass
    return samples


def watch(
    on_next_read: Callable[[dict], None],
    stop_event: threading.Event,
    sample_rate_ms: float,
    sample_fn: Callable[[], str | None],
    timestamp_field_name: str,
):
    last_sample_time = -1

    def on_new_read(new_samples: list[dict]):
        nonlocal last_sample_time
        delta_samples: list[dict] = []
        if len(new_samples) == 0:
            return
        for sample in new_samples:
            if sample[timestamp_field_name] > last_sample_time:
                delta_samples.append(sample)

        last_sample_time = new_samples[-1][timestamp_field_name]

        for sample in delta_samples:
            on_next_read(sample)

    sample_serial_monitor(
        on_new_read=on_new_read,
        timestamp_field_name=timestamp_field_name,
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
            logger.warning(f"[speak_with_serial_monitor fn] enqueued message is None")
            continue
        send_message_fn(message)


class SerialMonitorInterface:
    __slots__ = (
        "options",
        "messages_to_send_queue",
        "sender_thread",
        "watcher_thread",
        "stop_event",
    )

    def __init__(
        self,
        options: SerialMonitorOptions,
        on_next_read: Callable[[dict], None],
        messages_to_send_queue: QueueProtocol,
    ):
        self.messages_to_send_queue = messages_to_send_queue

        self.stop_event = threading.Event()

        self.options = options

        self.sender_thread = threading.Thread(
            target=partial(
                speak_with_serial_monitor,
                messages_queue=self.messages_to_send_queue,
                stop_event=self.stop_event,
                send_message_fn=self.options.interface.send_message,
            ),
            daemon=True,
        )
        self.watcher_thread = threading.Thread(
            target=partial(
                watch,
                on_next_read=on_next_read,
                stop_event=self.stop_event,
                timestamp_field_name=self.options.timestamp_field_name,
                sample_rate_ms=self.options.sample_rate_ms,
                sample_fn=self.options.interface.sample,
            ),
            daemon=True,
        )

    def __destroy__(self):
        self.stop()

    def send_message(self, message: str) -> None:
        self.messages_to_send_queue.put(message)

    def start(self) -> None:
        self.options.interface.start()
        self.sender_thread.start()
        self.watcher_thread.start()

    def stop(self) -> None:
        if self.sender_thread.is_alive():
            self.stop_event.set()
        self.options.interface.stop()
