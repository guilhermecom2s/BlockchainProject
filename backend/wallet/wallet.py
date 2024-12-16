import json
import uuid

from backend.config import STARTING_BALANCE
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec #ec stands for eliptic curve
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, #dss stands for disgital signature standard
    decode_dss_signature
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

class Wallet:
    """
    An individual wallet for a miner.
    Keeps track of the miner's balance.
    Allows a miner to authorize transactions.
    """

    def __init__(self, blockchain = None):
        self.blockchain = blockchain
        self.address = str(uuid.uuid4())[0:8] #In this case I'm using the uuid to generate unique values, but I can look at other ways to do so
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend) #The first parameter is the standard, and the second the backend beeing used
        self.public_key = self.private_key.public_key()
        self.serialize_public_key()

    @property
    #by creating a property for wallet I can create a code that runs every time this balance is accessed
    def balance(self):
        return Wallet.calculate_balance(self.blockchain, self.address)


    def sign(self, data):
        """
        Generate a signature based on the data using the local private key.
        """
        return decode_dss_signature(self.private_key.sign(
            json.dumps(data).encode('utf-8'), #The encode transforms the original string in its byte representation
            ec.ECDSA(hashes.SHA256())
            )) #I'm turing the byte string into it's decoded format

    def serialize_public_key(self):
        """
        Reset the public key to its serialized version.
        """
        self.public_key =  self.public_key.public_bytes( 
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8') #this will transform the public key into a byte then decode it 

    
    @staticmethod
    def verify(public_key, data, signature):
        """
        Verify  a signature based on the original public key data.
        """
        deserialize_public_key = serialization.load_pem_public_key(
            public_key.encode('utf-8'),
            default_backend()
        ) #need to turn the public_key back to it's deserializes form necause it won't work in it's string form

        (r, s) = signature #signature is a tuple with two values, I'm assigning the first to r and the second to s

        try:
            deserialize_public_key.verify(
                encode_dss_signature(r, s), #This method throws an exception when fail, that's why we use the try, catch
                json.dumps(data).encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
                )
            return True
        except InvalidSignature: #Getting the especifi exception
            return False

    @staticmethod
    def calculate_balance(blockchain, address):
        """
        Calculate the balance of the given address considering the transaction
        data within the blockchain.

        The balance is found by adding the output values that belong to the 
        address since the most recente transaction by that address
        """
        balance = STARTING_BALANCE

        if not blockchain: #in this case the given blockchain is None
            return balance #then I'll just return the balance as it is

        for block in blockchain.chain:
            for transaction in block.data: #what if not data is a transaction ?
                if transaction['input']['address'] == address: #if true the adress has conducted an transaction
                    #Any time the address conducts a new transaction it resets its balance
                    balance = transaction['output'][address]
                elif address in transaction['output']: #for the case the address is a recipient
                    balance += transaction['output'][address]

        return balance



def main():
    wallet = Wallet()
    print(f'wallet.__dict__: {wallet.__dict__}')

    data = {'foo' : 'bar'}
    signature = wallet.sign(data)
    print(f'signature: {signature}')

    should_be_valid = Wallet.verify(wallet.public_key, data, signature)
    print(f'should_be_valid: {should_be_valid}')

    should_be_invalid = Wallet.verify(Wallet().public_key, data, signature) #Should return false because I'm using a random public key from Wallet()
    print(f'should_be_invalid: {should_be_invalid}')

if __name__ == '__main__':
    main()