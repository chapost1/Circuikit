from .models import Sensors
import requests
import dataclasses
import signal
import sys


class ThingsBoardGateway:
    __slots__ = "token"

    def __init__(self, token: str):
        # IO libraries are tricky to handle on sigint
        # So we make sure we kill it
        def signal_handler(sig, frame):
            print("SIGINT received, exiting gracefully...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        self.token = token

    def on_new_read(self, new_read: Sensors) -> None:
        print(f"[ThingsBoardGateway] new_read={new_read}", flush=True)
        response = requests.post(
            url=f"http://thingsboard.cloud/api/v1/{self.token}/telemetry",
            json=dataclasses.asdict(new_read),
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
