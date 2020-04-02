#!/bin/bash
DB_FILE=~/sensordata.db
OUT_FILE=nohup.out
PYTHON_SCRIPT=htreadings-client.py

mkdir -p db
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" db/sensordata.db
else
    echo "no db file"
fi

if [ -f "$OUT_FILE" ]; then
    rm "$OUT_FILE"
fi

nohup python -u "$PYTHON_SCRIPT" &
echo "done"
