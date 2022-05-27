#include <ESP32Servo.h>
#include <Arduino.h>

// create four servo objects 
Servo doorServo;
Servo fanServo;

// Published values for SG90 servos; adjust if needed
int minUs = 500;
int maxUs = 2500;

int fanServoPin = 18;
int doorServoPin = 19;

int fanDelay = 2;
int doorDelay = 2;

// position in degrees
int pos = 0;  

unsigned long previousMillis = 0;

const long interval = 5000;

void setupDoor() {
	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	doorServo.setPeriodHertz(200);      // Standard 50hz servo
	fanServo.setPeriodHertz(200);      // Standard 50hz servo
}

bool changePos(Servo servo, int pos, int delaySeconds) {
	servo.write(pos);
	delay(delaySeconds);
	return true;
}

void openDoor() {
	doorServo.attach(doorServoPin, minUs, maxUs);
	for (pos = 90; pos >= 0; pos -= 1) {
		doorServo.write(pos);
		delay(fanDelay);
	}
	doorServo.detach();

	fanServo.attach(fanServoPin, minUs, maxUs);
	for (pos = 0; pos <= 90; pos += 1) {
		fanServo.write(pos);
		delay(doorDelay);
	}
	fanServo.detach();
}

void closeDoor() {
	fanServo.attach(fanServoPin, minUs, maxUs);
	for (pos = 90; pos >= 0; pos -= 1) {
		fanServo.write(pos);
		delay(fanDelay);
	}
	fanServo.detach();

	doorServo.attach(doorServoPin, minUs, maxUs);
	for (pos = 0; pos <= 90; pos += 1) {
		doorServo.write(pos);
		delay(doorDelay);
	}
	doorServo.detach();
}

// void moveServo(){
//     unsigned long currentMillis = millis();

// 	if (currentMillis - previousMillis >= interval)
// 	{
// 		previousMillis = currentMillis;
// 		servo.attach(servoPin, minUs, maxUs);
// 		for (pos = 0; pos <= 90; pos += 1) { // changes position to 0 degrees
// 			// in steps of 1 degree
// 			servo.write(pos);
// 			delay(10);             // waits 20ms for the servo to reach the position
// 		}
// 		for (pos = 90; pos >= 0; pos -= 1) { // sweep from 90 degrees to 0 degrees
// 			servo.write(pos);
// 			delay(1);
// 		}
// 		servo.detach();
// 	}
// }