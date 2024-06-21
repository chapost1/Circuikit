import sms_sender
from env import DESTINATION_PHONE_NUMBER
from models import UltrasonicRead


def on_new_read(new_read: UltrasonicRead):
    print(f"[AL]: {new_read}", flush=True)


# TODO: listen to some incidents file or something

if __name__ == "__main__":
    sms_sender.send(phone_number=DESTINATION_PHONE_NUMBER, message="I'm up")
