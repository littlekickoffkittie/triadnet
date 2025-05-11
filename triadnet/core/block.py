from dataclasses import dataclass, field
from typing import List, Optional
import time
from datetime import datetime
from .transaction import Transaction
from .fractal_coordinate import FractalCoordinate
import hashlib
import json

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    miner: str
    fractal_coord: FractalCoordinate
    previous_hash: str = field(default="0" * 64)
    hash: str = field(default="", init=False)
    nonce: int = field(default=0, init=False)
    
    def calculate_hash(self) -> str:
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.__dict__ for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "miner": self.miner,
            "fractal_coord": {
                "a": self.fractal_coord.a,
                "b": self.fractal_coord.b,
                "c": self.fractal_coord.c
            },
            "nonce": self.nonce
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
