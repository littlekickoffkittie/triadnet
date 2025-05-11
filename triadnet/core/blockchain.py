from typing import List, Optional
from datetime import datetime
import json
import logging
from .block import Block
from .transaction import Transaction
from .fractal_coordinate import FractalCoordinate

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        if not self.chain:
            self._create_genesis_block()
            
    def _create_genesis_block(self) -> None:
        genesis_coord = FractalCoordinate(a=0, b=0, c=0)
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow().timestamp(),
            transactions=[],
            previous_hash="0" * 64,
            miner="network",
            fractal_coord=genesis_coord
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        
    @property
    def last_block(self) -> Optional[Block]:
        return self.chain[-1] if self.chain else None
        
    def add_block(self, block: Block) -> bool:
        if not self._is_valid_block(block):
            return False
        self.chain.append(block)
        return True
        
    def add_pending_transaction(self, transaction: Transaction) -> None:
        self.pending_transactions.append(transaction)
        
    def _is_valid_block(self, block: Block) -> bool:
        if block.index != len(self.chain):
            return False
        if block.previous_hash != self.last_block.hash:
            return False
        if not block.hash.startswith("0" * self.difficulty):
            return False
        return True
        
    def is_valid_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.previous_hash != previous.hash:
                return False
            if not current.hash.startswith("0" * self.difficulty):
                return False
        return True
