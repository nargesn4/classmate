import adafruit_dht 
 
sensor = adafruit_dht.DHT22(20, False)
trash = ""

def readTemperatureInside():
  try:
    return sensor.temperature
  except Exception as e:
    trash = e
    print (e)


def readHumidityInside():
  try:
    return sensor.humidity
  except Exception as e:
    trash = e
    print (e)