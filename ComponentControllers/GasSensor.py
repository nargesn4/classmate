from gas_detection import GasDetection
from time import sleep

smoke_detector = GasDetection()
sleep(2)
ppm = smoke_detector.percentage()
smoke_value = ppm[smoke_detector.SMOKE_GAS]
print(smoke_value)
