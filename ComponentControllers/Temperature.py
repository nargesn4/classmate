import adafruit_dht 
 
sensor = adafruit_dht.DHT22(20)

def readTemperatureInside():
  try:
    return sensor.temperature
  except Exception as e:
    print('Inside Temperature Reading Failed')
    print (e)

def readHumidityInside():
  try:
    return sensor.humidity
  except Exception as e:
    print('Inside Humidity Reading Failed')
    print (e)