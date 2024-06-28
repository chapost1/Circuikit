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

PYTHON_APP_FILE_PATH=./app.py

if [ ! -f $PYTHON_APP_FILE_PATH ]; then
    echo "[ERROR] $PYTHON_APP_FILE_PATH does not exist."
    kill -9 $pid1
    exit 1
fi

python3 $PYTHON_APP_FILE_PATH
