from gas_detection import GasDetection
from time import sleep

#instantiate our GasDetection class.
smoke_detector = GasDetection()
#Wait 20 seconds for it to calibrate. This should be done in the fresh air.
sleep(2)
#This will return us an object of all gases and their concentrations in the air.
ppm = smoke_detector.percentage()
#chekking the smoke
smoke_value = ppm[smoke_detector.SMOKE_GAS]
#printing the value
print(smoke_value)
