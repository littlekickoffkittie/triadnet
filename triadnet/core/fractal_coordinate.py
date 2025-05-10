from dataclasses import dataclass
import random

@dataclass
class FractalCoordinate:
    a: float
    b: float
    c: float
    
    @classmethod
    def generate(cls):
        a = random.random()
        b = random.random()
        c = random.random()
        return cls(a, b, c)
