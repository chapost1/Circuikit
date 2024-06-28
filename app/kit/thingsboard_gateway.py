from app.models import Sensors
import requests
import dataclasses
import signal
import sys
import time
from app.kit.task import Task


def current_milli_time():
    return round(time.time() * 1000)


MAX_REQUESTS_PER_SECOND = 5


class ThingsBoardGateway(Task):
    def __init__(self, token: str):
        super().__init__()

        # IO libraries are tricky to handle on sigint
        # So we make sure we kill it
        def signal_handler(sig, frame):
            print("SIGINT received, exiting gracefully...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        self.token = token
        self.last_request_ts_ms = -1

    def on_message(self, message: Sensors) -> None:
        self.send_request(message=message)

    def send_request(self, message: Sensors):
        now_ms = current_milli_time()
        if (now_ms - self.last_request_ts_ms) < (1000 / MAX_REQUESTS_PER_SECOND):
            print("Too many requests per second, skipping post event")
            return
        self.last_request_ts_ms = now_ms
        response = requests.post(
            url=f"http://thingsboard.cloud/api/v1/{self.token}/telemetry",
            json=dataclasses.asdict(message),
        )
        if response.status_code > 299:
            print(
                f"[ThingsBoardGateway] failed to send; status_code={response.status_code}",
                flush=True,
            )
            print(response.json(), flush=True)
        else:
            print(
                f"[ThingsBoardGateway] message sent; status_code={response.status_code}",
                flush=True,
            )
