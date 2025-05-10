from dataclasses import dataclass, field
from typing import List, Any
from .block import Block

@dataclass
class Blockchain:
    chain: List[Block] = field(default_factory=list)

    def add_block(self, block: Block):
        self.chain.append(block)
