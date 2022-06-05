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

int fanDelay = 4;
int doorDelay = 4;

int doorLowPos = 0;
int doorHighPos = 90;

int fanLowPos = 0;
int fanHighPos = 90;

// position in degrees
int pos = 0;

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
	for (pos = doorHighPos; pos >= doorLowPos; pos -= 1) {
		doorServo.write(pos);
		delay(fanDelay);
	}
	doorServo.detach();

	fanServo.attach(fanServoPin, minUs, maxUs);
	for (pos = fanLowPos; pos <= fanHighPos; pos += 1) {
		fanServo.write(pos);
		delay(doorDelay);
	}
	fanServo.detach();
}

void closeDoor() {
	fanServo.attach(fanServoPin, minUs, maxUs);
	for (pos = fanHighPos; pos >= fanLowPos; pos -= 1) {
		fanServo.write(pos);
		delay(fanDelay);
	}
	fanServo.detach();

	doorServo.attach(doorServoPin, minUs, maxUs);
	for (pos = doorLowPos; pos <= doorHighPos; pos += 1) {
		doorServo.write(pos);
		delay(doorDelay);
	}
	doorServo.detach();
}