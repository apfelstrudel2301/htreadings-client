#!/bin/bash

cp ~/sensordata.db db/sensordata.db
rm nohup.out
nohup python htreadings-client.py &
echo "done"
