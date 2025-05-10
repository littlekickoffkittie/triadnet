from dataclasses import dataclass, field
import uuid

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    data: str
    tx_id: str = field(init=False)

    def __post_init__(self):
        self.tx_id = str(uuid.uuid4())
