import json
import sqlite3
import time
import datetime
import requests

INTERVAL = 300
DB_PATH = 'db/sensordata.db'
API_BASE_URL = 'https://eatpcfzrgg.execute-api.eu-central-1.amazonaws.com/int'
API_KEY = '1iXFG6qHJZ6C2CD1Ihvhv9s1tA2UYaXaDVZs9114'
GPIO = 4
MOCK_SENSOR_READINGS = False


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
            timestamp, temperature, humidity = record_and_save(gpio=GPIO, db_path=DB_PATH)
            recording_error = False
        except Exception as e:
            print('Recording error')
            print(e)
            recording_error = True
        if not recording_error:
            if push_latest_db_entries:
                print('Push latest database entries')
                # bulk_upload_successful = push_history(db_path=DB_PATH, api_url_bulk=api_url_bulk, headers=headers)
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
                # single_upload_successful = upload_entry(timestamp, temperature, humidity, api_url_single=api_url_single, headers=headers)
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
        time.sleep(INTERVAL)
        print('Done')


def record_and_save(gpio, db_path):
    if not MOCK_SENSOR_READINGS:
        import Adafruit_DHT
        sensor = Adafruit_DHT.DHT22
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
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
        print('Made entry to local db')
    else:
        timestamp = datetime.datetime.now()
        temperature = 23.4
        humidity = 56.7
    return timestamp, temperature, humidity


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


# def push_history(db_path, api_url_bulk, headers):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM (SELECT * FROM htreadings ORDER BY timestamp desc LIMIT 201) ORDER BY timestamp asc')
#     rows = cursor.fetchall()
#     conn.close()
#     entries_dict_list = [dict(zip(['id', 'timestamp', 'temperature', 'humidity'], values)) for values in rows]
#     payload = json.dumps(entries_dict_list)
#     try:
#         response = requests.request("POST", api_url_bulk, headers=headers, data=payload)
#     except requests.exceptions.ConnectionError as e:
#         print('Could not create connection to REST endpoint for bulk upload')
#         print(e)
#         return False
#     time.sleep(0.1)
#     if response.status_code != 200:
#         print('bulk upload error')
#         print(response.text.encode('utf8'))
#         return False
#     if response.status_code == 200:
#         print(len(entries_dict_list))
#         print('Successfully pushed history')
#         return True
#
#
# def upload_entry(timestamp, temperature, humidity, api_url_single, headers):
#     data = {
#         'timestamp': datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S.%f"),
#         'temperature': temperature,
#         'humidity': humidity
#     }
#     payload = json.dumps(data)
#     try:
#         response = requests.request("POST", api_url_single, headers=headers, data=payload)
#     except requests.exceptions.ConnectionError as e:
#         print('Could not create connection to REST endpoint for single upload.')
#         print(e)
#         return False
#     time.sleep(0.1)
#     if response.status_code != 200:
#         print('Upload error')
#         print(response.text.encode('utf8'))
#         return False
#     if response.status_code == 200:
#         print('Upload successful')
#         return True


if __name__ == '__main__':
    main()

