# ClassMate
## Configuration / Settings
In the settings.py adjust the application root directory to match the application path of your classmate directory. For the ESP32's, adjust the WiFi and host-ip settings in `./CPP_WebSockets/main.cpp`.

## Communication: WebSockets
The system runs on 1 Raspberry Pi and 2 ESP32's. WebSockets are used to communicate between devices / clients.

The general idea is that there's a WebSocket server (`./webserver.py`) which acts as a message hub and pushes a received message to all connected clients. That way, when some client sends some data, all clients get that message instantly and can decide for themselves whether or not they want to act on it.
When running, there should be at least 4 clients:
- Dashboard (Website, available on http://{rpi-ipaddress}:8888/)
- Door&Fan ESP32 (ESP32 controlling 2 servo's and a fan)
- Air quality ESP32 (ESP32 measuring temperature & humidity)
- Logic (python script that connects certain data to actions in a smart way)

Setup:
- On your Raspberry Pi, run both `classmate/ws_server.py` (WebSockets server & Dashboard host) and `classmate/main.py` (Logic client). 
- On the Door&Fan ESP32, write the file `./ESP32s/src/servo/servo.cpp` to the ESP using PlatformIO (more detailed description can be found below)
- On the Air quality ESP32, write the file `./ESP32s/src/temperature/temperature.cpp` to the ESP using PlatformIO.

All WebSocket messages are in JSON and should look the following:
```
{
    "client_id": string,        (like "CLIENT_ID_ESP_DOOR" or "CLIENT_ID_LOGIC"),
    "action": string,           (like "ACTION_ALIVE" or "ACTION_CHAT")
    "data": any                 (depends on the action what kind of data should be passed)
} 
```

## Data storage: TinyDB
For storing sets of data [TinyDB](https://tinydb.readthedocs.io/en/latest/) is used as this is sufficient enough for fine our prototype. For example, the TinyDB `logs.json` is filled with all messages.

## RgbLed
Takes an RGB LED and three 100 Ohm resistors, obviously aside from the usual cables.

## Speaker
Class made for controlling a Speaker using an I2S board (specifically the `MAX98357`).

Connect pins as following:
```
    5V      -> Vin
    GND     -> GND
    PIN18   -> BCLK
    PIN19   -> LRC
    PIN21   -> DIN
```

Then do `sudo nano /boot/config.txt`, and comment the `dtparam=audio=on` line and add two new lines, resulting in among other things:
```
    # dtparam=audio=on
    dtoverlay=hifiberry-dac
    dtoverlay=i2s-mmap
```

Create a new file using `sudo nano /etc/asound.conf`, and add the following contents:

```
pcm.hifiberry {
type hw card 0
}

pcm.!default {
type plug
slave.pcm "dmixer"
}

pcm.dmixer {
type dmix
ipc_key 1024
slave {
pcm "hifiberry"
channels 2
}
}
```

Then, execute the following two commands:

```
sudo apt-get install vlc
sudo pip3 install python-vlc
```

## CO2 sensor
cabling:
```
5V on RPi and Vin on mh-z19
GND(0v) on RPi and GND on mh-z19
TxD and RxD are connected to cross between RPi and mh-z18
```

For enabling serial port run:
```
sudo sed -i "s/^enable_uart=.*/enable_uart=1/" /boot/config.txt
```
Install sensor:
```
sudo pip3 install mh_z19
```
To use mh-z19, once you need to set up enabling serial port device on the Raspberry Pi. Follow this [Wiki]( https://github.com/UedaTakeyuki/mh-z19/wiki/How-to-Enable-Serial-Port-hardware-on-the-Raspberry-Pi) page to do that.

### read CO2 Sensor value
```
python Co2Sensor.py
```
You should see something like this: 
```
{'co2': 668}
```

## DHT11 sensor (temperature and humidity)
Sensor setup from left to right
```
1st pin = pin 14
2nd pin = ground
3rd pin = vcc 3.3V
```

Download the following extension:
Pymakr

How to install micropython on the esp32
```
# Download esptool
git clone https://github.com/espressif/esptool.git -b v2.8
cd esptool
# Erase flash. Press the reset button while Connecting.
python3 esptool.py --chip esp32 --port /dev/ttyUSB* erase_flash
# Download the latest firmware release
https://micropython.org/download/esp32/ 
# Upload firmware to board
python3 esptool.py --chip esp32 --port /dev/ttyUSB* --baud 460800 write_flash -z 0x1000 ** drop the firmware file in here **
```

## Sound
Connect the sound sensor pins as following (from left to right):
```
analog  -> pin 17
GND     -> GND
VCC     -> 5V
```

## Gas sensor
### wiring

from GPIO2 goes to LV1 and then from HV1 continues to SDA of ADS1115.

Yellow wire from GPIO3 goes to LV2 and then from HV2 continues to SCL of ADS1115.

MQ2's A0 (analog) pin is connected to A0 on ADS1115.

Enable the I2C interface on our RPi, which is disabled by default. To enable I2C type:

```
sudo raspi-config
```
Under Interfacing Options enable I2C. You might need to do sudo reboot here.

Now in the command line type:
```
i2cdetect -y  1
```
This outputs a table with the list of detected devices on the I2C bus.

### Riquired library

gas-detection library. To install it run this command: 
```
pip install gas-detection==1.0.1
```
Next type in the terminal:
```
python app.py
```
You should see something like this: 
```
0.02436100935984771
```

