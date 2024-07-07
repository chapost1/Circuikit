import requests
import time
from .service import Service
import logging

logger = logging.getLogger(__name__)


def current_milli_time():
    return round(time.time() * 1000)


MAX_REQUESTS_PER_SECOND = 5


class ThingsBoardGateway(Service):
    def __init__(self, token: str):
        super().__init__()

        self.token = token
        self.last_request_ts_ms = -1

    def on_message(self, message: dict) -> None:
        self.send_request(json=message)

    def send_request(self, json: dict):
        now_ms = current_milli_time()
        if (now_ms - self.last_request_ts_ms) < (1000 / MAX_REQUESTS_PER_SECOND):
            logger.warning("Too many requests per second, skipping post event")
            return
        self.last_request_ts_ms = now_ms
        response = requests.post(
            url=f"http://thingsboard.cloud/api/v1/{self.token}/telemetry",
            json=json,
        )
        if response.status_code > 299:
            logger.error(f"failed to send; status_code={response.status_code}")
            try:
                logger.debug(f"response={response.json()}")
            except requests.exceptions.JSONDecodeError:
                logger.error(f"response={response.text}")
        else:
            logger.debug(f"message sent; status_code={response.status_code}")
