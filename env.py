import os

def get_or_set(name: str, default: str) -> str:
    return os.getenv(name) or default

def get_or_exit(name: str):
    val = os.getenv(name)
    if val is None:
        print(f'os[{name}] is not found. exit...')
        exit(1)
    return val

SAMPLE_RATE_MS = float(get_or_set('SAMPLE_RATE_MS', '5.0'))

THINKERCAD_URL = get_or_exit('THINKERCAD_URL')
DEBUGGER_PORT = int(get_or_exit('DEBUGGER_PORT'))

DESTINATION_PHONE_NUMBER = get_or_exit('DESTINATION_PHONE_NUMBER')
