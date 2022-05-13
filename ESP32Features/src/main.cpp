#include "CPP_WebSockets/CPP_WebSockets.hpp"
#include "servo/servo.hpp"
#include "temperature/temperature.hpp"

unsigned long measurementPrevMillis = 0;
const unsigned long measurementIntervalMs = 3000;

void setup() {
	Serial.begin(115200);
	setupWebsocket("CLIENT_ID_ESP_TEMPERATURE_HUMIDITY_DOOR");
	setupTemperature();
	setupServo();
}

void loop() {

    if (millis() - measurementPrevMillis >= measurementIntervalMs) {
        measurementPrevMillis = millis();
		float temperature = readTemperature();
		float humidity = readHumidity();

		if (temperature < 0 || humidity < 0) {
			Serial.println(F("Error reading temperature and humidity!"));
		}
		else {
			humidity /= 100;
			temperature /= 100;
			Serial.print(F("Temperature: "));
			Serial.print(temperature);
			Serial.println(F("°C"));
			Serial.print(F("Humidity: "));
			Serial.print(humidity);
			Serial.println(F("%"));
			sendData("ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE", "{\"temperature\": \"" + String(temperature) + "\", \"humidity\": \"" + String(humidity) + "\"}");
			// sendMessage("Temperature Measured " + String(temperature) + " " + String(humidity));
		}
	}
	moveServo();
    websocketLoop();
}
