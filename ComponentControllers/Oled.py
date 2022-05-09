import I2C_LCD_driver
import RPi.GPIO as GPIO
from time import *

mylcd = I2C_LCD_driver.lcd()

state = False

def button_callback(channel):
    global state
    state = state != True
    if state == False:
        mylcd.lcd_display_string("Geen mode actief", 1)
    else:
        mylcd.lcd_display_string("Niet Storen mode", 1)


GPIO.setwarnings(False) #Ignore Warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(13,GPIO.FALLING,callback=button_callback)
message= input("Press enter to quit\n\n")
GPIO.cleanup()

