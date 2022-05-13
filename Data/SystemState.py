import json
from dataclasses import dataclass

@dataclass
class SystemState:
    temperature_outside: int = 0
    humidity_outside: int = 0