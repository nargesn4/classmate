import RPi.GPIO as GPIO

"""
class made for controlling a do-not-disturb-light using an RGB Led (100R registors from each GPIO pin to LED pin)
before calling this class, set pin numbering mode via GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)
initialize this class like:
        rgbLed = RgbLed(RED_PIN,GREEN_PIN,BLUE_PIN)
then use the rgbLed using
        rgbLed.doNotDisturb()
or:
        rgbLed.turnOfDoNotDisturb()
or
        rgbLed.clearAll()
"""
class RgbLed:
        # integer RED_PIN       (GPIO pin the Red LED pin is connected to)
        # integer GREEN_PIN     (GPIO pin the Green LED pin is connected to)
        # integer BLUE_PIN      (GPIO pin the Blue LED pin is connected to)
    def __init__(self,RED_PIN,GREEN_PIN,BLUE_PIN):
        self.R = RED_PIN
        self.G = GREEN_PIN
        self.B = BLUE_PIN
        GPIO.setup(self.R, GPIO.OUT)
        GPIO.setup(self.G, GPIO.OUT)
        GPIO.setup(self.B, GPIO.OUT)
    
    def doNotDisturb(self):
        self.clearAll()
        GPIO.output(self.R, GPIO.HIGH)
        
    def turnOffDoNotDisturb(self):
        self.clearAll()
        
    def clearAll(self):
        GPIO.output(self.R, GPIO.LOW)
        GPIO.output(self.G, GPIO.LOW)
        GPIO.output(self.B, GPIO.LOW)
   
   
   
# example code
# GPIO.setmode(GPIO.BCM)
# rgbLed = RgbLed(21,20,16)

# rgbLed.doNotDisturb()
# time.sleep(2)
# rgbLed.turnOffDoNotDisturb()