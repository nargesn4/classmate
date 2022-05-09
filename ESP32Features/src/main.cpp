#include "CPP_WebSockets/CPP_WebSockets.hpp"
#include "servo/servo.hpp"
#include "temperature/temperature.hpp"

void setup() {
	Serial.begin(115200);
	setupWebsocket();
	setupTemperature();
	setupServo();
}

void loop() {
	readTempAndHumidity();
	moveServo();
    websocketLoop();
}
