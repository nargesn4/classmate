from machine import Pin
from time import sleep
import dht 
 
led = Pin(2, Pin.OUT)
sensor = dht.DHT11(Pin(14))

while True:
  try:
    led.value(not led.value())
    sleep(2)
    sensor.measure()
    t = sensor.temperature()
    h = sensor.humidity()
    print('Temperature: %3.1f C' %t)
    print('Humidity: %3.1f %%' %h)
  except OSError as e:
    print('Sensor Reading Failed')