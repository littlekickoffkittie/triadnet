from triadnet import Transaction, generate_transactions, mine_block

def test_generate_transactions():
    txs = generate_transactions(5)
    assert len(txs) == 5
    assert all(isinstance(tx, Transaction) for tx in txs)
    assert isinstance(txs[0].tx_id, str) and len(txs[0].tx_id) > 0

def test_mine_block():
    txs = generate_transactions(3)
    block = mine_block(txs, 'prev_hash')
    assert block.previous_hash == 'prev_hash'
    assert len(block.transactions) == 3

def test_blockchain():
    txs = generate_transactions(2)
    block = mine_block(txs, 'genesis')
