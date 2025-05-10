import os
import hashlib
import time
import json
import base64
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from triadnet.models import FractalCoordinate, Transaction

class Wallet:
    def __init__(self, load_path: str = None):
        """Initialize a wallet with new or loaded keys and a fractal coordinate"""
        if load_path and os.path.exists(load_path):
            self._load_wallet(load_path)
        else:
            # Generate keypair using actual asymmetric cryptography
            self._generate_keypair()
            self.fractal_coord = FractalCoordinate.generate()
            # Generate address from public key
            self.address = self._generate_address()
            # Initialize balance and transaction history
            self.balance = 0.0
            self.transactions = []
            
    def _generate_keypair(self) -> None:
        """Generate a proper RSA keypair for signatures"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        self.private_key = private_key
        self.public_key = private_key.public_key()
        
        # Store serialized versions for easier storage
        self._private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        self._public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def _generate_address(self) -> str:
        """Generate a wallet address from the public key and fractal coordinate"""
        public_key_bytes = self._public_pem
        fractal_str = str(self.fractal_coord).encode()
        
        # First hash combines public key with fractal coordinate
        intermediate = hashlib.sha256(public_key_bytes + fractal_str).digest()
        
        # Second hash for added security (similar to Bitcoin's double-hash)
        address_bytes = hashlib.sha256(intermediate).digest()
        
        # Format as base58-like encoding (simplified here with base64)
        address = "TX" + base64.b32encode(address_bytes).decode()[:32]
        
        return address

    def sign_transaction(self, tx: Transaction) -> Transaction:
        """Sign a transaction with the wallet's private key"""
        # Create message from transaction data
        message = (
            f"{tx.tx_id}{tx.sender}{tx.receiver}{tx.amount}{tx.data}{tx.timestamp}"
        ).encode()
        
        # Sign the message using proper RSA signature
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Base64 encode the signature for storage
        tx.signature = base64.b64encode(signature).decode()
        return tx
        
    def create_transaction(self, receiver: str, amount: float, data: str = "") -> Transaction:
        """Create and sign a new transaction"""
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")
            
        if self.balance < amount:
            raise ValueError("Insufficient funds")
            
        tx = Transaction(
            tx_id=f"tx-{int(time.time())}-{os.urandom(4).hex()}",
            sender=self.address,
            receiver=receiver,
            amount=amount,
            data=data,
            timestamp=time.time()
        )
        
        # Sign the transaction
        return self.sign_transaction(tx)
    
    def verify_transaction(self, tx: Transaction) -> bool:
        """Verify a transaction's signature using the sender's public key (mainly for demonstration)"""
        # This would normally need to retrieve the sender's public key from a directory or chain
        # Here it's just showing the verification process using own key
        
        if tx.sender != self.address:
            # In a real system, you'd look up the sender's public key
            return False
            
        message = (
            f"{tx.tx_id}{tx.sender}{tx.receiver}{tx.amount}{tx.data}{tx.timestamp}"
        ).encode()
        
        try:
            # Decode the base64 signature
            signature = base64.b64decode(tx.signature)
            
            # Verify the signature
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False
    
    def save(self, path: str) -> None:
        """Save wallet to a file (warning: unencrypted)"""
        wallet_data = {
            "address": self.address,
            "private_key": self._private_pem.decode(),
            "public_key": self._public_pem.decode(),
            "fractal_coord": self.fractal_coord.to_dict(),
            "balance": self.balance,
            "transactions": [json.loads(tx.serialize()) for tx in self.transactions]
        }
        
        with open(path, 'w') as f:
            json.dump(wallet_data, f, indent=2)
    
    def _load_wallet(self, path: str) -> None:
        """Load wallet from a file"""
        with open(path, 'r') as f:
            wallet_data = json.load(f)
        
        # Load keys
        self._private_pem = wallet_data["private_key"].encode()
        self._public_pem = wallet_data["public_key"].encode()
        
        # Load private and public key objects
        self.private_key = serialization.load_pem_private_key(
            self._private_pem,
            password=None
        )
        self.public_key = serialization.load_pem_public_key(
            self._public_pem
        )
        
        # Load other attributes
        self.address = wallet_data["address"]
        self.fractal_coord = FractalCoordinate.from_dict(wallet_data["fractal_coord"])
        self.balance = wallet_data["balance"]
        
        # Load transaction history
        self.transactions = []
        for tx_data in wallet_data.get("transactions", []):
            self.transactions.append(Transaction.deserialize(json.dumps(tx_data)))
    
    def update_balance(self, blockchain) -> float:
        """Update wallet balance from blockchain"""
        self.balance = blockchain.get_balance(self.address)
        return self.balance
    
    def get_public_key_str(self) -> str:
        """Get the public key in PEM format for sharing"""
        return self._public_pem.decode()