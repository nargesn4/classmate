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