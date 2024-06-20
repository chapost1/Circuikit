import serial_monitor_watcher
import sms_sender
from sample import Sample

from env import (
    DESTINATION_PHONE_NUMBER
)

def on_new_samples(samples: list[Sample]):
    print(samples)

sms_sender.send(phone_number=DESTINATION_PHONE_NUMBER, message='I\'m up')
serial_monitor_watcher.watch(notify=on_new_samples)
