from triadnet import Transaction, FractalCoordinate

def test_transaction():
    tx = Transaction('sender1', 'receiver1', 10.0, 'data1')
    assert isinstance(tx.tx_id, str) and len(tx.tx_id) > 0

def test_fractal_coordinate():
    fc = FractalCoordinate(0.5, 0.3, 0.7)
    assert fc.a == 0.5
    assert fc.b == 0.3
    assert fc.c == 0.7

def test_generate_fractal():
    fc = FractalCoordinate.generate()
    assert 0 <= fc.a <= 1
    assert 0 <= fc.b <= 1
    assert 0 <= fc.c <= 1
