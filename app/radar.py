from .models import Sensors


class Radar:
    def on_new_read(self, new_read: Sensors):
        print(f"[RADAR]: {new_read}", flush=True)
