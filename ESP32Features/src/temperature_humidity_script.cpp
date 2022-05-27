// #include "CPP_WebSockets/CPP_WebSockets.hpp"
// #include "temperature_and_humidity/temperature_and_humidity.hpp"

// unsigned long measurementPrevMillis = 0;
// const unsigned long measurementIntervalMs = 3000;

// void actionHandler(String action) {
//     // Temperature sensor shouldn't act on anything. It should just report sensor data.
// }

// void setup() {
// 	Serial.begin(115200);
// 	setupWebsocket("CLIENT_ID_ESP_TEMPERATURE_HUMIDITY", actionHandler);
// 	setupTemperature();
// }

// void loop() {
//     if (millis() - measurementPrevMillis >= measurementIntervalMs) {
//         measurementPrevMillis = millis();
// 		float temperature = readTemperature();
// 		float humidity = readHumidity();

// 		if (temperature >= 0 && humidity >= 0) {
// 			humidity /= 100;
// 			temperature /= 100;
// 			sendData("ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE", "{\"temperature\": \"" + String(temperature) + "\", \"humidity\": \"" + String(humidity) + "\"}");
// 		}
// 		else
// 			Serial.println(F("Error reading temperature and humidity!"));
// 	}

//     websocketLoop(actionHandler);
// }
