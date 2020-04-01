#!/bin/bash

mkdir -p db
cp ~/sensordata.db db/sensordata.db
rm nohup.out
nohup python -u htreadings-client.py &
echo "done"
