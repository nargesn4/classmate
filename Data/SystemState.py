import json
from dataclasses import dataclass

from numpy import double

@dataclass
class SystemState:
    temperature_inside: float = 20
    humidity_inside: float = 50
    temperature_outside: float = 20
    humidity_outside: float = 50
    co2: int = 700
    co: int = 0
    smoke: int = 0
    noisy_outside: bool = False
    door_open: bool = False
    do_not_disturb: bool = None
    busy_in_15_minutes: bool = False
    favorable_conditions: bool = True
    points_co2: float = 0
    points_temperature: float = 0
    points_humidity: float = 0
    points_noise: float = 0
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    # def toJSON(self):
    #     return json.dumps({"temperature_inside": self.temperature_inside,
    #                        "humidity_inside": self.humidity_inside,
    #                        "temperature_outside": self.temperature_outside,
    #                        "humidity_outside": self.humidity_outside,
    #                        "co2": self.co2,
    #                        "noisy_outside": self.noisy_outside,
    #                        "door_open": self.door_open})