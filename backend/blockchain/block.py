import time

from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binary
from backend.config import MINE_RATE

#setting GENESIS_DATA as a global variable, that's why it's upper case 
GENESIS_DATA = {
    'timestamp': 1,
    'last_hash' : 'genesis_last_hash',
    'hash': 'genesis_hash',
    'data': [], 
    'difficulty' : 3,
    'nonce' : 'genesis_nonce'
}

class Block:
    """
    Block: a unit of storage.
    Store transactions in a blockchain that supports a cryptocurrency
    """
    def __init__(self, timestamp, last_hash, hash, data, difficulty, nonce):
        self.timestamp = timestamp
        self.last_hash = last_hash
        self.hash = hash
        self.data = data
        self.difficulty = difficulty #ammount of zeros in the beggining of the hash
        self.nonce = nonce

    def __repr__(self): #representation
        return (
            'Block('
            f'timestamp: {self.timestamp}, '
            f'last_hash: {self.last_hash}, '
            f'hash: {self.hash}, '
            f'data: {self.data}, '
            f'difficulty: {self.difficulty}, '
            f'nonce: {self.nonce})'
        )
    
    def __eq__(self, other): #the comparison is made between the instance of the object(self) and another object(other)
        # if I just compare two objects I'll get false even when they are equal, but I can compare what is 
        #inside the object with __dict__
        return self.__dict__ == other.__dict__
    
    def to_json(self):
        """
        Serialize the block into a dictionary of its attributes.
        """
        return self.__dict__

    #although they don't use the self parameter it's still cleaner to have them as static inside the Block class
    @staticmethod
    def mine_block(last_block, data):
        """
        Mine a block based on the given last_block and data, until a block hash
        is found that meets the leading 0's proof of work requirement.
        """
        timestamp = time.time_ns()
        last_hash = last_block.hash
        difficulty = Block.adjust_difficulty(last_block, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        #will keep running until the number of zeros in the beggining matches the required one
        while hex_to_binary(hash)[0:difficulty] != '0' * difficulty:
            nonce += 1
            timestamp = time.time_ns() #to assure the time is as accurate as possible
            difficulty = Block.adjust_difficulty(last_block, timestamp)
            hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        return Block(timestamp, last_hash, hash, data, difficulty, nonce)

    @staticmethod
    def genesis():
        """
        Generate the genesis block.
        """
        return Block(**GENESIS_DATA) #this sintax unpacks the entire GENESIS_DATA as indviduals arguments

    @staticmethod
    def from_json(block_json):
        """
        Deserialize a block's json representation back into a block instance.
        """
        return Block(**block_json)


    @staticmethod
    def adjust_difficulty(last_block, new_timestamp):
        """
        Calculate the adjusted difficulty according to the MINE_RATE.
        Increase the difficulty for quickly mined block.
        Decrease the difficulty for slowly mined blocks.
        """

        if (new_timestamp - last_block.timestamp) < MINE_RATE:
            return last_block.difficulty + 1

        if (last_block.difficulty - 1) > 0: #to prevent going bellow zero, which would be a problem
            return last_block.difficulty - 1

        return 1 #the default difficulty will be one
    
    @staticmethod
    def is_valid_block(last_block, block):
        """
        Validate block by enforcing the following rules:
            -the block must have the proper last_hash reference
            -the block must meet the proof of worj requirement
            -the difficuulty must only adjust by 1
            -the block hash must be a valid combination of the block fields
        """

        if block.last_hash != last_block.hash:
            raise Exception('The block last_hash must be correct!')
        
        if hex_to_binary(block.hash)[0:block.difficulty] != '0' * block.difficulty: #I'm working with the binary representation
            raise Exception('The proof of work requirement was not met!')
        
        if abs(last_block.difficulty - block.difficulty) > 1: #absolute value so it doesn't matter if it is a negative number
            raise Exception('The block difficulty must only adjust by 1')
        
        reconstructed_hash = crypto_hash( #Be careful with the order of the arguments if the sort function is not beeing used
            block.timestamp,
            block.last_hash,
            block.data,
            block.nonce,
            block.difficulty
        )

        if block.hash != reconstructed_hash:
            raise Exception('The block hash must be corret')


    
def main():    
    genesis_block = Block.genesis()
    bad_block = Block.mine_block(Block.genesis(), 'foo')
    bad_block.last_hash = 'evil_data'

    try: #doing a try catch so the code won't brake if the excpetion occurs
        Block.is_valid_block(genesis_block, bad_block)
    except Exception as e:
        print(f'is_valid_block: {e}')

if __name__ == '__main__': #if i'm executing this class I'll get the __main as it's name and return the experimental code, otherwise not
    main()