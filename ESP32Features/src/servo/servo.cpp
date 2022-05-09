#include <ESP32Servo.h>
#include <Arduino.h>

// create four servo objects 
Servo servo;

// Published values for SG90 servos; adjust if needed
int minUs = 500;
int maxUs = 2400;

int servoPin = 14;

// position in degrees
int pos = 0;  

unsigned long previousMillis = 0;

const long interval = 5000;

void setupServo() {
	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	servo.setPeriodHertz(200);      // Standard 50hz servo
}

void moveServo(){
    unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
    servo.attach(servoPin, minUs, maxUs);
	for (pos = 0; pos <= 90; pos += 1) { // changes position to 0 degrees
		// in steps of 1 degree
		servo.write(pos);
		delay(10);             // waits 20ms for the servo to reach the position
	}
	for (pos = 90; pos >= 0; pos -= 1) { // sweep from 90 degrees to 0 degrees
		servo.write(pos);
		delay(1);
	}
	servo.detach();
  }
}