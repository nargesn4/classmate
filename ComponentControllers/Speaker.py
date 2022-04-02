import RPi.GPIO as GPIO
import time
import vlc


"""
Class made for controlling a Speaker using an I2S board (specifically the MAX98357).

Connect the pins as following:
    5V      -> Vin
    GND     -> GND
    PIN18   -> BCLK
    PIN19   -> LRC
    PIN21   -> DIN

Then do     sudo nano /boot/config.txt  , and comment the dtparam=audio=on line and add two new lines, resulting in among other things:
    # dtparam=audio=on
    dtoverlay=hifiberry-dac
    dtoverlay=i2s-mmap
    
Create a new file using     sudo nano /etc/asound.conf  , and add the following contents:

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


Then, execute the following two commands:
    sudo apt-get install vlc 
    sudo pip3 install python-vlc



In your code, initialize this class like:
        speaker = Speaker(FILE_PATH, VOLUME)
then use the speaker by using
        speaker.play()
and/or
        speaker.pause()
"""
class Speaker:
    # integer VOLUME        (in domain of [0,100])
    # string FILE_PATH
    def __init__(self, VOLUME, FILE_PATH):
        instance = vlc.Instance('--aout=alsa')
        self.p = instance.media_player_new()
        self.m = instance.media_new(FILE_PATH) 
        self.p.set_media(self.m)
        vlc.libvlc_audio_set_volume(self.p, VOLUME)
    
    def play(self):
        self.p.play()
    
    def pause(self):
        self.p.pause()
   
# example code
doNotDisturbActivated = Speaker(60, "Resources/Audio/Testing/do_not_disturb_activated.mp3")
doNotDisturbDeactivated = Speaker(60, "Resources/Audio/Testing/do_not_disturb_deactivated.mp3")
demoAudio = Speaker(100, "Resources/Audio/Testing/demo_audio.mp3")

doNotDisturbActivated.play()
time.sleep(2)
doNotDisturbActivated.pause()
doNotDisturbDeactivated.play()
time.sleep(2)
doNotDisturbDeactivated.pause()
demoAudio.play()
time.sleep(5)
demoAudio.pause()
