# htreadings-client
The client software for recording DHT22 sensor readings with a Raspberry Pi and sending them to an API (e.g. for displaying the data in a dashboard).

## Getting started

### Prerequisites
- DHT22 sensor connected to Raspberry Pi
- Raspbian Buster operating system (if you have to upgrade from stretch check out this [upgrade tutorial](https://pimylifeup.com/upgrade-raspbian-stretch-to-raspbian-buster))

### Install dependencies

Install the Python dependencies
```bash
pip install -r requirements.txt
```

Installl the libgiod2 library needed by the [CircuitPython Libraries](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup).
```bash
sudo apt-get install libgpiod2
```

### Configure sensor readings script
Configure the following attributes in [htreadings-client.py](htreadings-client.py):
- API endpoint
- API_KEY
- d

### Start script
Start recording sensor readings and sending them to an API

- Install Adafruit package from 
- Configure gpio of the DHT22 sensor in `htreadings-client.py`


```bash
```