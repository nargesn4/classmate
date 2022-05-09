import RPi.GPIO as GPIO
import time

HCSR04_OUT = 27
HCSR04_IN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(HCSR04_OUT, GPIO.OUT)
GPIO.setup(HCSR04_IN, GPIO.IN)

def get_distance():

    GPIO.output(HCSR04_OUT, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(HCSR04_OUT, GPIO.LOW)

    while GPIO.input(HCSR04_IN) == GPIO.LOW:
        start = time.time()

    while GPIO.input(HCSR04_IN) == GPIO.HIGH:
        end = time.time()
    
    sig_time = end-start()

    distance = sig_time / 0.000058
    return distance

print(get_distance())


