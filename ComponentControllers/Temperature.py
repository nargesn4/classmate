import adafruit_dht 
import board
 
sensor = adafruit_dht.DHT22(board.D23, False)
trash = ""

def readTemperatureInside():
  try:
    return sensor.temperature
  except Exception as e:
    trash = e
    # print (e)


def readHumidityInside():
  try:
    return sensor.humidity
  except Exception as e:
    trash = e
    # print (e)