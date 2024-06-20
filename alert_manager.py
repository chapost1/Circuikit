import sms_sender
from env import (
    DESTINATION_PHONE_NUMBER
)

sms_sender.send(phone_number=DESTINATION_PHONE_NUMBER, message='I\'m up')

# TODO: listen to some incidents file or something
