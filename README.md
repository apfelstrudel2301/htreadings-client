# htreadings-client
The client software for recording DHT22 sensor readings with a Raspberry Pi and sending them to an API (e.g. for displaying the data in a dashboard).

## Getting started

### Prerequisites
- DHT22 sensor connected to Raspberry Pi
- Raspbian Buster operating system (if you have to upgrade from stretch check out this [upgrade tutorial](https://pimylifeup.com/upgrade-raspbian-stretch-to-raspbian-buster))

### Install dependencies

Install the Python dependencies
```bash
pip3 install -r requirements.txt
```

Installl the libgiod2 library needed by the [CircuitPython Libraries](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup).
```bash
sudo apt-get install libgpiod2
```

### Configure sensor readings script
The following attributes in [htreadings-client.py](htreadings-client.py) have to be configured individually:
- API_BASE_URL: String containing the API URL for 
- API_KEY: API key of the API
- DHT_DEVICE: You might need to change this configuration if you don't use a DHT22 sensor and if it is not connected to pin 4 on the raspberry pi. Check out [CircuitPython Libraries](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup) for possible configurations.

### Start script
Start recording sensor readings and sending them to an API by executing the startup script:
```bash
chmod +x startup_htreadings_client.sh
```

```bash
./startup_htreadings_client.sh
```

## Misc
Formerly the [Adafruit_DHT](https://github.com/adafruit/Adafruit_Python_DHT) package was used for recoriding the sensor values.