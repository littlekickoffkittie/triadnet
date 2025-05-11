import hashlib
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    data: str = ""
    timestamp: float = time.time()
    tx_id: Optional[str] = None
    signature: Optional[str] = None

    def __post_init__(self):
        if self.tx_id is None:
            self.tx_id = self.calculate_hash()

    def calculate_hash(self) -> str:
        tx_string = f"{self.sender}{self.receiver}{self.amount}{self.data}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()
