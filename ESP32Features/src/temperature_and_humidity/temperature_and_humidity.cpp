#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 19  

#define DHTTYPE    DHT11     // DHT 11

DHT_Unified dht(DHTPIN, DHTTYPE);

void setupTemperature() {
  // Initialize device.
  dht.begin();
}

// Temperature gets returned as an integer * 100, for more accurate readings. Returning a float changed the value of the float.
int readTemperature() {
  sensors_event_t event;
  dht.temperature().getEvent(&event);

  if (isnan(event.temperature))
    return -1;
  else
    return event.temperature * 100;
}

int readHumidity() {
  sensors_event_t event;
  dht.humidity().getEvent(&event);

  if (isnan(event.relative_humidity))
    return -1;
  else
    return event.relative_humidity * 100;
}