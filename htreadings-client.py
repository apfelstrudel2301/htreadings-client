import json
import sqlite3
import time
import datetime
import requests


def main():
    #TODO: set to false
    mock_sensor_readings = False
    if not mock_sensor_readings:
        import Adafruit_DHT
        sensor = Adafruit_DHT.DHT22
        gpio = 4
    interval = 300
    db_path = 'db/sensordata.db'
    api_url = 'https://t2sa88ddol.execute-api.eu-central-1.amazonaws.com/dev/htreadings'
    i = 0
    delta = False
    while True:
        try:
            if mock_sensor_readings:
                timestamp = datetime.datetime.now()
                temperature = 23.0
                humidity = 45.7
            else:
                timestamp, temperature, humidity = record_and_save(sensor=sensor, gpio=gpio, db_path=db_path)
            rec_error = False
        except Exception as e:
            print(e)
            rec_error = True
            print('Recording error')
        if not rec_error:
            if delta:
                print('recover delta')
                push_successful = push_history(db_path=db_path, api_url=api_url)
                if push_successful:
                    delta = False
            else:
                upload_successful = upload_entry(timestamp, temperature, humidity, api_url=api_url)
                if upload_successful:
                    i += 1
                    print('sent values ' + str(i))
                else:
                    print('connection error')
                    delta = True
        time.sleep(interval)
        print('Done')


def record_and_save(sensor, gpio, db_path):
    import Adafruit_DHT
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    timestamp = datetime.datetime.now()
    print(timestamp)
    print('Temperature: {0:0.1f}*C, Humidity: {1:0.1f}%'.format(temperature, humidity))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO htreadings (timestamp, temperature, humidity) VALUES (?, ?, ?)',
                   (timestamp, temperature, humidity))
    conn.commit()
    conn.close()
    print('Made entry to local db')
    return timestamp, temperature, humidity


def push_history(db_path, api_url):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM (SELECT * FROM htreadings ORDER BY timestamp desc LIMIT 210) ORDER BY timestamp asc')
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        _, timestamp, temperature, humidity = row
        upload_successful = upload_entry(timestamp, temperature, humidity, api_url=api_url)
        if not upload_successful:
            return False
    conn.close()
    print('Successfully pushed history')
    return True


def upload_entry(timestamp, temperature, humidity, api_url):
    data = {
        'timestamp': datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f"),
        'temperature': temperature,
        'humidity': humidity
    }
    payload = json.dumps(data)
    url = api_url
    headers = {
        'x-api-key': 'vS6Cq6hlVX2UWqnfKKTne6T5JkkTNsl4aSkdzPL4',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    time.sleep(0.1)
    if response.status_code != 200:
        print('upload error')
        print(response.text.encode('utf8'))
        return False
    if response.status_code == 200:
        print('uploaded successfully')
        return True


if __name__ == '__main__':
    main()

