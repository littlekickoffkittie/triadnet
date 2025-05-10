import gmpy2
from hashlib import sha256

P = 2**256 - 2**32 - 977
FIELD = gmpy2.mpz(P)
CHAOTIC_R = gmpy2.mpz(3990000)

def chaotic_map(x: gmpy2.mpz, r: gmpy2.mpz = CHAOTIC_R) -> gmpy2.mpz:
    x_scaled = x % FIELD
    term = (x_scaled * (FIELD - x_scaled)) % FIELD
    return (r * term) % FIELD

def hash_in_field(data: bytes, seed: gmpy2.mpz = None) -> gmpy2.mpz:
    raw_hash = sha256(data).digest()
    field_val = gmpy2.mpz(int.from_bytes(raw_hash, 'big')) % FIELD
    return chaotic_map(field_val, seed if seed else field_val)
