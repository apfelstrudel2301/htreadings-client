import json
import sqlite3
import time
import datetime
import requests
import adafruit_dht
import board

# Measurement interval in seconds
INTERVAL = 300
DB_PATH = 'db/sensordata.db'
API_BASE_URL = 'https://eatpcfzrgg.execute-api.eu-central-1.amazonaws.com/int'
API_KEY = '1iXFG6qHJZ6C2CD1Ihvhv9s1tA2UYaXaDVZs9114'
GPIO = 4
MOCK_SENSOR_READINGS = False


def get_sensor_reading(gpio, db_path):
    if not MOCK_SENSOR_READINGS:
        # import Adafruit_DHT
        # sensor = Adafruit_DHT.DHT22
        # humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
        temperature = humidity = None
        while not (temperature and humidity):
            try:
                dht_device = adafruit_dht.DHT22(board.D4)
                print('initialized dht_device')
                temperature = dht_device.temperature
                print(temperature)
                humidity = dht_device.humidity
                print(humidity)
                timestamp = datetime.datetime.now()
                print(timestamp)
                print('Temperature: {0:0.1f}*C, Humidity: {1:0.1f}%'.format(temperature, humidity))
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS htreadings (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp '
                               'DATETIME, temperature NUMERIC, humidity NUMERIC)')
                cursor.execute('INSERT INTO htreadings (timestamp, temperature, humidity) VALUES (?, ?, ?)',
                               (timestamp, temperature, humidity))
                conn.commit()
                conn.close()
                print('Made entry to local database')
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print('Error reading the sensor')
                print(error.args[0])
                print('-------------------------------------------------')
            time.sleep(5)
    else:
        timestamp = datetime.datetime.now()
        temperature = 23.4
        humidity = 56.7
    return timestamp, temperature, humidity


def main():
    api_url_single = API_BASE_URL + '/htreadings-single'
    api_url_bulk = API_BASE_URL + '/htreadings-bulk'
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    iteration_count = 0
    # Used in case of errors to recover the delta between the local and remote data
    push_latest_db_entries = True
    while True:
        try:
            timestamp, temperature, humidity = get_sensor_reading(gpio=GPIO, db_path=DB_PATH)
            recording_error = False
        except Exception as e:
            print('Recording error')
            print(e)
            recording_error = True
        if not recording_error:
            if push_latest_db_entries:
                print('Push latest database entries')
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM (SELECT * FROM htreadings ORDER BY timestamp desc LIMIT 201) ORDER BY timestamp asc')
                rows = cursor.fetchall()
                conn.close()
                entries_dict_list = [dict(zip(['id', 'timestamp', 'temperature', 'humidity'], values)) for values in
                                     rows]
                bulk_upload_successful = upload(api_url=api_url_bulk, headers=headers, data=entries_dict_list)
                if bulk_upload_successful:
                    print('Successfully pushed history with ' + str(len(entries_dict_list)) + ' values')
                    push_latest_db_entries = False
                else:
                    print('Bulk upload failed.')
            else:
                data = {
                    'timestamp': datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f"),
                    'temperature': temperature,
                    'humidity': humidity
                }
                single_upload_successful = upload(api_url=api_url_single, headers=headers, data=data)
                if single_upload_successful:
                    iteration_count += 1
                    print('Sent values ' + str(iteration_count))
                else:
                    print('Single upload failed.')
                    push_latest_db_entries = True
        print('Iteration complete')
        time.sleep(INTERVAL)


def upload(api_url, headers, data):
    payload = json.dumps(data)
    try:
        response = requests.request("POST", api_url, headers=headers, data=payload)
    except requests.exceptions.ConnectionError as e:
        print('Could not create connection to REST endpoint ' + api_url)
        print(e)
        return False
    time.sleep(0.1)
    if response.status_code != 200:
        print('Upload error')
        print(response.text.encode('utf8'))
        return False
    if response.status_code == 200:
        return True


if __name__ == '__main__':
    main()

