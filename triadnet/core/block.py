from dataclasses import dataclass, field
from typing import List, Any
import hashlib

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Any]
    previous_hash: str
    hash: str = field(init=False)

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()
