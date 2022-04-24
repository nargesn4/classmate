# ClassMate
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



