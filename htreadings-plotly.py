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

def tick():
    i=0
    s1.open()
    s2.open()
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
        # humidity, temperature = (i, i+1)
        timestamp = datetime.datetime.now()
        print('Temperature: {0:0.1f}*C, Humidity: {1:0.1f}%'.format(temperature, humidity))

        conn = sqlite3.connect('../sensordata-stream.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO htreadings (timestamp, temperature, humidity) VALUES (?, ?, ?)', (timestamp, temperature, humidity))
        conn.commit()
        conn.close()
        print('Made entry')

        s1.write(dict(x=timestamp, y=temperature))
        s2.write(dict(x=timestamp, y=humidity))
        i += 1
        print('Sent values ' + str(i))
        time.sleep(30)


tick()
s1.close()
s2.close()
print('closed')
