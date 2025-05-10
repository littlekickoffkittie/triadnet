import gmpy2
import time
import hashlib
import random
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

from triadnet.models.models import Transaction, FractalCoordinate, Block, Blockchain

# Set up constants for consensus
FIELD = gmpy2.mpz(2**256)
DEFAULT_DIFFICULTY = 4  # Number of leading zeros required
BLOCK_REWARD = 10.0
TARGET_BLOCK_TIME = 60  # Target time in seconds between blocks
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # Adjust difficulty every X blocks
MAX_TRANSACTIONS_PER_BLOCK = 100

# Configure logging
logger = logging.getLogger("consensus")

@dataclass
class MiningResult:
    """Class to hold mining result data"""
    success: bool
    hash_val: str
    nonce: int
    duration: float
    block: Optional[Block] = None


class ProofOfFractalWork:
    """Enhanced Proof of Fractal Work consensus mechanism"""
    
    def __init__(self, difficulty: int = DEFAULT_DIFFICULTY):
        self.difficulty = difficulty
        self.target = "0" * difficulty  # Target is X leading zeros
        
    def adjust_difficulty(self, blockchain: Blockchain) -> None:
        """Adjust difficulty based on recent block times"""
        if len(blockchain.chain) <= DIFFICULTY_ADJUSTMENT_INTERVAL:
            return
            
        # Get the last adjustment interval blocks
        recent_blocks = blockchain.chain[-DIFFICULTY_ADJUSTMENT_INTERVAL:]
        first_block_time = recent_blocks[0].timestamp
        last_block_time = recent_blocks[-1].timestamp
        
        # Calculate the actual time it took to mine these blocks
        actual_time_taken = last_block_time - first_block_time
        expected_time = TARGET_BLOCK_TIME * DIFFICULTY_ADJUSTMENT_INTERVAL
        
        # Adjust difficulty if mining is too fast or too slow
        ratio = actual_time_taken / expected_time
        
        if ratio > 2.0:
            # Mining too slow, decrease difficulty
            if self.difficulty > 1:
                self.difficulty -= 1
                logger.info(f"Decreased difficulty to {self.difficulty}")
        elif ratio < 0.5:
            # Mining too fast, increase difficulty
            self.difficulty += 1
            logger.info(f"Increased difficulty to {self.difficulty}")
            
        # Update target
        self.target = "0" * self.difficulty
    
    def mine(self, block: Block, max_iterations: int = 10000000) -> MiningResult:
        """Mine a block using Proof of Fractal Work"""
        start_time = time.time()
        
        # A proper mining algorithm considers block content and fractal coordinate
        fractal_factor = self._calculate_fractal_factor(block.fractal_coord)
        
        for nonce in range(max_iterations):
            # Set the nonce
            block.nonce = nonce
            
            # Calculate hash
            block_hash = block.calculate_hash()
            
            # Apply fractal factor to modify difficulty locally
            required_zeros = max(1, self.difficulty + fractal_factor)
            local_target = "0" * required_zeros
            
            # Check if hash meets target
            if block_hash.startswith(local_target[:self.difficulty]):
                duration = time.time() - start_time
                block.hash = block_hash
                
                logger.info(f"Block mined! Hash: {block_hash[:10]}..., Nonce: {nonce}, Time: {duration:.3f}s")
                
                return MiningResult(
                    success=True,
                    hash_val=block_hash,
                    nonce=nonce,
                    duration=duration,
                    block=block
                )
        
        # If we reach here, we didn't find a valid nonce
        duration = time.time() - start_time
        logger.warning(f"Mining failed after {max_iterations} iterations ({duration:.3f}s)")
        
        return MiningResult(
            success=False,
            hash_val="",
            nonce=0,
            duration=duration
        )
    
    def _calculate_fractal_factor(self, coord: FractalCoordinate) -> int:
        """Calculate a difficulty factor based on fractal coordinates
        
        This creates areas in the fractal space that are easier or harder to mine,
        encouraging strategic positioning of nodes.
        """
        # Use the fractal coordinates to influence mining difficulty
        # This example creates "hot spots" in the fractal space
        
        # Calculate distance from multiple "hot spots"
        hotspots = [
            FractalCoordinate(a=100, b=100, c=100),
            FractalCoordinate(a=500, b=500, c=500),
            FractalCoordinate(a=300, b=700, c=200)
        ]
        
        # Find minimum distance to any hotspot
        min_distance = min(coord.distance(spot) for spot in hotspots)
        
        # Adjust factor based on distance (closer = easier)
        if min_distance < 50:
            return 1  # Easier
        elif min_distance < 200:
            return 0  # Normal
        else:
            return -1  # Harder
    
    def validate_block(self, block: Block) -> bool:
        """Validate a mined block"""
        # Recalculate the hash
        calculated_hash = block.calculate_hash()
        
        # Check if the hash matches the one in the block
        if calculated_hash != block.hash:
            logger.warning(f"Block hash mismatch: {calculated_hash} vs {block.hash}")
            return False
        
        # Verify the hash meets difficulty requirement
        if not block.hash.startswith(self.target):
            logger.warning(f"Block hash doesn't meet difficulty requirement: {block.hash}")
            return False
        
        return True


class ConsensusManager:
    """Manager for blockchain consensus operations"""
    
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.pofw = ProofOfFractalWork(difficulty=blockchain.difficulty)
    
    def create_block(self, miner_address: str, 
                    fractal_coord: FractalCoordinate) -> Block:
        """Create a new block with pending transactions"""
        # Get pending transactions (up to limit)
        transactions = self.blockchain.pending_transactions[:MAX_TRANSACTIONS_PER_BLOCK]
        
        # Create block
        block = Block(
            index=len(self.blockchain.chain),
            timestamp=time.time(),
            transactions=transactions,
            prev_hash=self.blockchain.last_block.hash,
            miner=miner_address,
            fractal_coord=fractal_coord
        )
        
        return block
    
    def mine_block(self, block: Block, max_iterations: int = 10000000) -> MiningResult:
        """Mine a block and add it to blockchain if valid"""
        # Mine the block
        result = self.pofw.mine(block, max_iterations)
        
        if result.success:
            # Add the block to the chain
            self.blockchain.chain.append(result.block)
            
            # Clear mined transactions from pending
            for tx in result.block.transactions:
                if tx in self.blockchain.pending_transactions:
                    self.blockchain.pending_transactions.remove(tx)
            
            # Add mining reward transaction
            reward_tx = Transaction(
                tx_id=f"reward-{int(time.time())}",
                sender="network",
                receiver=block.miner,
                amount=BLOCK_REWARD,
                data="Mining reward",
                timestamp=time.time()
            )
            self.blockchain.add_transaction(reward_tx)
            
            # Adjust difficulty if needed
            if block.index % DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
                self.pofw.adjust_difficulty(self.blockchain)
                self.blockchain.difficulty = self.pofw.difficulty
        
        return result
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
        if len(self.blockchain.chain) == 0:
            return True
            
        # Validate genesis block separately
        genesis = self.blockchain.chain[0]
        if genesis.index != 0 or genesis.prev_hash != "0" * 64:
            logger.error("Invalid genesis block")
            return False
            
        # Validate each block in the chain
        for i in range(1, len(self.blockchain.chain)):
            current = self.blockchain.chain[i]
            previous = self.blockchain.chain[i-1]
            
            # Check block connection
            if current.prev_hash != previous.hash:
                logger.error(f"Invalid chain at block {i}: Broken link")
                return False
                
            # Check block hash validity
            if not self.pofw.validate_block(current):
                logger.error(f"Invalid chain at block {i}: Invalid hash")
                return False
                
            # Check block index continuity
            if current.index != previous.index + 1:
                logger.error(f"Invalid chain at block {i}: Index mismatch")
                return False
        
        return True


# Legacy function for backward compatibility
def pofw_mine(transactions: list[Transaction], coord: FractalCoordinate, 
              depth: int, prev_hash: gmpy2.mpz, max_iterations: int) -> Tuple[gmpy2.mpz, int, float]:
    """Legacy mining function for backward compatibility"""
    start_time = time.time()
    target = FIELD // gmpy2.mpz(500)  # Lowered difficulty
    
    for i in range(max_iterations):
        nonce = gmpy2.mpz(i)
        data = (
            str([t.tx_id + t.data for t in transactions]).encode(),
            str(coord.a).encode(),
            str(coord.b).encode(),
            str(coord.c).encode(),
            str(depth).encode(),
            str(prev_hash).encode(),
            str(nonce).encode()
        )
        hash_input = b''.join(data)
        hash_val = gmpy2.mpz(int.from_bytes(hashlib.sha256(hash_input).digest(), 'big'))
        
        if hash_val < target:
            duration = time.time() - start_time
            return hash_val, int(nonce), duration
            
    duration = time.time() - start_time
    return gmpy2.mpz(0), 0, duration
