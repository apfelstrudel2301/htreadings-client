#!/bin/bash

cp ~/sensordata.db /db/sensordata-stream.db
rm nohup.out
( nohup python htreadings-client.py & )
echo "done"
