#!/usr/bin/python

import math # because the Americans can't spell
import sqlite3 as sql
import time
import datetime
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

import Adafruit_DHT
import sqlite3


stream_ids = tls.get_credentials_file()['stream_ids']

sensor = Adafruit_DHT.DHT22
gpio = 4
interval = 300

temp_trace = Scatter(
    x = [],
    y = [],
    mode = 'lines+markers',
    name = 'Temp',
    stream = Stream(
        token=stream_ids[0]
    )
)

hum_trace = Scatter(
    x = [],
    y = [],
    mode = 'lines+markers',
    name = 'Hum',
    stream = Stream(
        token=stream_ids[1]
    )
)

data = Data([temp_trace, hum_trace])
layout = Layout(
    title = 'Indoor Temperature & Humidity',
    yaxis = YAxis(
        title = 'Temperature'
    ),
    yaxis2 = YAxis(
        title = 'Humidity',
        overlaying = 'y',
        side = 'right'
    ),
    showlegend=True,
    legend=Legend(
        x=0,
        y=0
    )
)
fig = Figure(data = data, layout = layout)
unique_url = py.plot(fig, filename='Indoor_temp_hum', auto_open=False)
print(unique_url)
s1 = py.Stream(stream_ids[0])
s2 = py.Stream(stream_ids[1])

def push_history():
    s1.open()
    s2.open()
    conn = sqlite3.connect('../sensordata-stream.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM (SELECT * FROM htreadings ORDER BY timestamp desc LIMIT 510) ORDER BY timestamp asc')
    while True:
	row = cursor.fetchone()
        if row == None:
            break
        _, timestamp, temperature, humidity = row
        s1.write(dict(x=timestamp, y=temperature))
        s2.write(dict(x=timestamp, y=humidity))
	time.sleep(0.1)
    conn.close()
    s1.close()
    s2.close()
    return


def tick():
    i=0
    delta = False
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
        # humidity, temperature = (i, i+1)
        timestamp = datetime.datetime.now()
	print(timestamp)
        print('Temperature: {0:0.1f}*C, Humidity: {1:0.1f}%'.format(temperature, humidity))

        conn = sqlite3.connect('../sensordata-stream.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO htreadings (timestamp, temperature, humidity) VALUES (?, ?, ?)', (timestamp, temperature, humidity))
        conn.commit()
        conn.close()
        print('Made entry')
	try:
	    if delta:
		print('recover delta')
		push_history()
	    	delta = False
	    else:
		s1.open()
		s2.open()
                s1.write(dict(x=timestamp, y=temperature))
            	s2.write(dict(x=timestamp, y=humidity))
            	i += 1
            	print('sent values ' + str(i))
	    	s1.close()
	    	s2.close()
	except:
	    print('connection error')
	    delta = True
        time.sleep(interval)

push_history()
tick()
s1.close()
s2.close()
print('closed')

