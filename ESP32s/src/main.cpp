#include "temperature/temperature.hpp"
#include "servo/servo.hpp"
    
void setup() {
	Serial.begin(115200);
	setupTemperature();
	setupServo();
}

void loop() {
	readTempAndHumidity();
	moveServo();
}
