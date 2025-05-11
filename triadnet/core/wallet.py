import hashlib
import time
from typing import Optional

class Wallet:
    def __init__(self, private_key: Optional[str] = None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = hashlib.sha256(str(time.time()).encode()).hexdigest()
        self.address = f"TRIAD{hashlib.sha256(self.private_key.encode()).hexdigest()[:40]}"
