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