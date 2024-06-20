import serial_monitor_watcher
from sample import Sample

def on_new_samples(samples: list[Sample]):
    print(samples)

serial_monitor_watcher.watch(notify=on_new_samples)
