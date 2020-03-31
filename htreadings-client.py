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
    api_url = 'https://0bdk4n5198.execute-api.eu-central-1.amazonaws.com/int/htreadings-single'
    api_url_bulk = 'https://0bdk4n5198.execute-api.eu-central-1.amazonaws.com/int/htreadings-bulk'
    headers = {
        'x-api-key': 'lIdPMMnhF81773ppFUa1f74sup3dmLjA9zgABZF5',
        'Content-Type': 'application/json'
    }
    i = 0
    delta = True
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
                push_successful = push_history(db_path=db_path, api_url=api_url_bulk, headers=headers)
                if push_successful:
                    delta = False
            else:
                upload_successful = upload_entry(timestamp, temperature, humidity, api_url=api_url, headers=headers)
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


def push_history(db_path, api_url, headers):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM (SELECT * FROM htreadings ORDER BY timestamp desc LIMIT 201) ORDER BY timestamp asc')
    rows = cursor.fetchall()
    conn.close()
    entries_dict_list = [dict(zip(['id', 'timestamp', 'temperature', 'humidity'], values)) for values in rows]
    payload = json.dumps(entries_dict_list)
    try:
        response = requests.request("POST", api_url, headers=headers, data=payload)
    except requests.exceptions.ConnectionError as e:
        print('Could not create connection to REST endpoint for bulk upload')
        print(e)
        return False
    time.sleep(0.1)
    if response.status_code != 200:
        print('bulk upload error')
        print(response.text.encode('utf8'))
        return False
    if response.status_code == 200:
        print(len(entries_dict_list))
        print('Successfully pushed history')
        return True


def upload_entry(timestamp, temperature, humidity, api_url, headers):
    data = {
        'timestamp': datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f"),
        'temperature': temperature,
        'humidity': humidity
    }
    payload = json.dumps(data)
    url = api_url
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.ConnectionError as e:
        print('Could not create connection to REST endpoint')
        print(e)
        return False
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

