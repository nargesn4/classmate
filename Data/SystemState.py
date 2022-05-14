import json
from dataclasses import dataclass

@dataclass
class SystemState:
    temperature_inside: int = 0
    humidity_inside: int = 0
    temperature_outside: int = 0
    humidity_outside: int = 0
    co2: int = 0
    noisy_outside: bool = False
    door_open: bool = False
    
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