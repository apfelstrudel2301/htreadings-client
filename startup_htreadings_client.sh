#!/bin/bash
DB_DIR=db
DB_FILE=sensordata.db
DB_FILE_EXISTING=~/sensordata.db
OUT_FILE=nohup.out
PYTHON_SCRIPT=htreadings-client.py

mkdir -p "$DB_DIR"
if [ -f "$DB_FILE_EXISTING" ]; then
    cp "$DB_FILE_EXISTING" "$DB_DIR"/"$DB_FILE"
fi

if [ -f "$OUT_FILE" ]; then
    rm "$OUT_FILE"
fi

nohup python -u "$PYTHON_SCRIPT" &
echo "done"
