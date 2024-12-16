from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD_INPUT

class Blockchain:
    """
    Blockchain: a public ledger of transactions
    Implemented as a list of block - data sets of transactions
    """

    def __init__(self):
        self.chain = [Block.genesis()]

    def add_block(self, data):
        self.chain.append(Block.mine_block(self.chain[-1], data)) #self.chain[-1] returns me the last block in the chain

    def __repr__(self):  # so it won't return it memory adress
        return f'Blockchain: {self.chain}'
    
    def replace_chain(self, chain):
        """
        Replace the local chain with the incoming one if the following applies:
            - The incoming chain is longer than the local one.
            - The incoming chain is formatted properly
        """
        if len(chain) <= len(self.chain):
            raise Exception('Cannot replace. The incoming chain must be longer.')

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e: #e is an instance of Exception
            raise Exception(f'Cannot replace. The incoming chain is invalid: {e}')
        
        self.chain = chain # if the two conditions above are met I assign the new chain to be the 'local' one

    def to_json(self):
        """
        Serialize the blockchain into a list of blocks.
        """
        #the map funtion will produce a list taking another list as an input applying an operation to ther former one
        return list(map(lambda block: block.to_json(), self.chain)) #the first parameter is the function and the second is the list

    @staticmethod
    def from_json(chain_json):
        """
        Deserialize a list of serialized blocks into a Blockchain instance.
        The result will contain a chain list of Block instances.
        """
        blockchain = Blockchain()
        blockchain.chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))

        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate the incoming chain.
        Enforce the following rules of the blockchain:
            - the chain must start with the genesis block
            - blocks must be formated correctly
        """
        if chain[0] != Block.genesis(): #here it'll use the __eq__ method to compare the two of them
            raise Exception('The genesis block must be valid')


        for i in range(1, len(chain)): #I'll skip the genesis block
            block = chain[i]
            last_block = chain[i-1]
            Block.is_valid_block(last_block, block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce the rules of a chain composed of blocks of transactions.
            - Each transaction must only appear once in the chain.
            - There can only be one mining reward per block.
            - Each transaction must be valid.
        """
        transactions_ids = set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transactions_ids:
                    raise Exception(f'Transaction {transaction.id} is not unique')
                
                transactions_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(
                            'There cna only be one mining reward per block. '\
                            f'Check block with hash: {block.hash}'
                        )
                    
                    has_mining_reward = True
                else: #A reward doesn't have an input amount, with this else the tests won't fail
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain [0:i]
                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain,
                        transaction.input['address']
                    )

                    if historic_balance != transaction .input['amount']:
                        raise Exception('has an invalid input amount')
                        #raise Exception(
                        #    f'Transaction {transaction.id} has an invalid'\
                        #    'input amount'
                        #) #this Excpetion was returning a regex error when comparing the input with the regex

                Transaction.is_valid_transaction(transaction)


def main():
    blockchain = Blockchain()
    blockchain.add_block('one')
    blockchain.add_block('two')

    print(blockchain)
    print(f'blockchain.py __name__: {__name__}')


if __name__ == '__main__':  # if i'm executing this class I'll get the __main as it's name and return the experimental code, otherwise not
    main()
