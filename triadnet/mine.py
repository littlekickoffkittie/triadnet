from triadnet.core import Transaction, FractalCoordinate
import random
import time

def generate_transactions(num_transactions: int) -> list[Transaction]:
    txs = []
    for i in range(num_transactions):
        tx = Transaction(
            sender=f'sender{i}',
            receiver=f'receiver{i}',
            amount=random.uniform(1, 100),
            data=f'data{i}'
        )
        txs.append(tx)
    return txs

def mine_block(transactions, prev_hash):
    from triadnet.core import Block
    return Block(
        index=0,
        timestamp=time.time(),
        transactions=transactions,
        previous_hash=prev_hash
    )
