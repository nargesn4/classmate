
import mh_z19
import time
from ComponentControllers.Speaker import Speaker
from ComponentControllers.Temperature import readTemperatureInside, readHumidityInside

s = Speaker(50, "Resources/Audio/Testing/demo_audio.mp3")
s.playForTime(5)
# s.play()
# time.sleep(2)
# s.pause()
# temperature_inside = readTemperatureInside()
# print (temperature_inside)
# smoke_value_string = str(mh_z19.read_co2valueonly())
# print (smoke_value_string)
