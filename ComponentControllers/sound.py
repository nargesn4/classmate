import RPi.GPIO as GPIO
import time

# GPIO setup
channel = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
startTime = time.time()


def callback(channel):
    timePassed = time.time() - startTime
    print("sound detected! Time passed = ", timePassed)


GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

while True:
    time.sleep(1)
