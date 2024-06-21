#!/bin/bash

DIRTY_PATH=./dirty
source $DIRTY_PATH/venv/bin/activate

PORT=8989

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=$PORT --user-data-dir=$DIRTY_PATH/chrome-profile &
# apparently, can't get pid regularly
pid1=$(lsof -n -i :$PORT | grep LISTEN | grep Google | awk '{print $2}')

LOGS_PATH=$DIRTY_PATH/logs
mkdir -p $LOGS_PATH

export READINGS_LOG_FILE_PATH=$LOGS_PATH/readings.log
rm -rf $READINGS_LOG_FILE_PATH
touch $READINGS_LOG_FILE_PATH

export SAMPLE_RATE_MS=5.0
export THINKERCAD_URL=https://www.tinkercad.com/things/eCe35FTAbqM-brave-hillar-bombul/editel
export DEBUGGER_PORT=$PORT
export DESTINATION_PHONE_NUMBER=+972526982308

python index.py &
pid2=$!

trap clear SIGHUP SIGINT SIGTERM

function clear {
    kill -9 $pid1
    kill -9 $pid2
    exit
}

wait $pid1 $pid2
