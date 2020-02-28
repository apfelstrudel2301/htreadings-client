#!/bin/bash

cp ~/sensordata.db ~/htreadings-client/db/sensordata-stream.db
rm ~/htreadings-client/nohup.out
( cd ~/htreadings-client && nohup python ~/htreadings-client/htreadings-client.py & )
echo "done"
