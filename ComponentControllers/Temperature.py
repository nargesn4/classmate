import adafruit_dht 
 
sensor = adafruit_dht.DHT22(20)
trash = ""

def readTemperatureInside():
  try:
    return sensor.temperature
  except Exception as e:
    trash = e


def readHumidityInside():
  try:
    return sensor.humidity
  except Exception as e:
    trash = e