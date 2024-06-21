from models import UltrasonicRead


def on_new_read(new_read: UltrasonicRead):
    print(f"[RADAR]: {new_read}")
