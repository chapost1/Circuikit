import requests
import signal
import sys
import time
from .service import Service


def current_milli_time():
    return round(time.time() * 1000)


MAX_REQUESTS_PER_SECOND = 5


class ThingsBoardGateway(Service):
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

    def on_message(self, message: dict) -> None:
        self.send_request(json=message)

    def send_request(self, json: dict):
        now_ms = current_milli_time()
        if (now_ms - self.last_request_ts_ms) < (1000 / MAX_REQUESTS_PER_SECOND):
            print("Too many requests per second, skipping post event")
            return
        self.last_request_ts_ms = now_ms
        response = requests.post(
            url=f"http://thingsboard.cloud/api/v1/{self.token}/telemetry",
            json=json,
        )
        if response.status_code > 299:
            print(
                f"[ThingsBoardGateway] failed to send; status_code={response.status_code}",
                flush=True,
            )
            try:
                print(response.json(), flush=True)
            except requests.exceptions.JSONDecodeError:
                print(response.text, flush=True)
        else:
            print(
                f"[ThingsBoardGateway] message sent; status_code={response.status_code}",
                flush=True,
            )
