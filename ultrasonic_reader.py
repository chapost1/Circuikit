import serial_monitor_watcher
from models import UltrasonicRead
import json
import dataclasses

from env import (
    READINGS_FILE_PATH
)

if __name__ == '__main__':
    with open(READINGS_FILE_PATH, "a") as incidents_file:

        def on_new_reads(readings: list[UltrasonicRead]):
            for read in readings:
                incidents_file.write(f'{json.dumps(dataclasses.asdict(read))}\n')

        serial_monitor_watcher.watch(notify=on_new_reads)
