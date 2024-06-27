#!/bin/bash

DIRTY_PATH=./dirty
mkdir -p $DIRTY_PATH

VENV_PATH=$DIRTY_PATH/venv

if [ -d $VENV_PATH ]; then
  echo "venv exists."
  source $VENV_PATH/bin/activate
else
  echo "venv does not exists. setting it up".
  python3 -m venv $VENV_PATH
  source $VENV_PATH/bin/activate
  pip install -r requirements.txt
fi

ENV_FILE_PATH=$DIRTY_PATH/env.py

if [ ! -f $ENV_FILE_PATH ]; then
    echo "[ERROR] $ENV_FILE_PATH does not exist. please create it and populate it with variables. otherwise functionality won't work."
    echo "Please create it and populate it with needed variables."
    echo "Otherwise system functionality won't work."
    exit 1
fi

PORT=8989

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=$PORT --user-data-dir=$DIRTY_PATH/chrome-profile &
# apparently, can't get pid regularly
pid1=$(lsof -n -i :$PORT | grep LISTEN | grep Google | awk '{print $2}')

export DEBUGGER_PORT=$PORT

python3 index.py &
pid2=$!

trap clear SIGHUP SIGINT SIGTERM

function clear {
    kill -9 $pid1
    kill -9 $pid2
    exit
}

wait $pid1 $pid2
