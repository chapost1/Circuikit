import time
import os
import json
from env import READINGS_FILE_PATH, INCIDENTS_FILE_PATH

from models import UltrasonicRead


def follow(file_descriptor):
    """generator function that yields new lines in a file"""
    # seek the end of the file
    file_descriptor.seek(0, os.SEEK_END)

    # start infinite loop
    while True:
        # read last line of file
        line = file_descriptor.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line


if __name__ == "__main__":
    readings = follow(file_descriptor=open(READINGS_FILE_PATH, "r"))
    # iterate over the generator
    for line in readings:
        read = UltrasonicRead(**json.loads(line))
        print(read)
        if False:
            with open(INCIDENTS_FILE_PATH, "a") as incidents_file:
                incidents_file.write('{"hello": "world"}\n')
