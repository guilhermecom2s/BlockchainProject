import pytest

from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import GENESIS_DATA
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction

def test_blockchain_instance():
    blockchain = Blockchain()

    #checking if the first block is indeed the genesis one
    assert blockchain.chain[0].hash == GENESIS_DATA['hash']

def test_add_block():
    blockchain = Blockchain()
    data = 'test-data'
    blockchain.add_block(data)

    #checking if the last block is indeed the last added block
    assert blockchain.chain[-1].data == data

@pytest.fixture
def blockchain_three_blocks():
    blockchain = Blockchain()
    for i in range(3): #arbitrary number of times it will iterate
        blockchain.add_block([Transaction(Wallet(), 'recipient', i).to_json()]) #I'll add three arbitrary blocks to the chain that will allow me to test if the chain is valid
    return blockchain

def test_is_Valid_chain(blockchain_three_blocks):
    Blockchain.is_valid_chain(blockchain_three_blocks.chain)

def test_is_valid_chain_bad_genesis(blockchain_three_blocks):
    blockchain_three_blocks.chain[0].hash = 'evil_hash' #changing the hash of the genesis block

    with pytest.raises(Exception, match= 'The genesis block must be valid'):
        Blockchain.is_valid_chain(blockchain_three_blocks.chain)

def test_replace_chain(blockchain_three_blocks):
    blockchain = Blockchain()
    blockchain.replace_chain(blockchain_three_blocks.chain)

    #I'll assert that the new chain will be the blockchain_tree_blocks.chain
    assert blockchain.chain == blockchain_three_blocks.chain

def test_replace_chain_not_longer(blockchain_three_blocks):
    blockchain = Blockchain()

    with pytest.raises(Exception, match = 'Cannot replace. The incoming chain must be longer.'):
        #won't work because blockchain just has the genesis block, so it's smaller
        blockchain_three_blocks.replace_chain(blockchain.chain)

def test_replace_chain_bad_chain(blockchain_three_blocks):
    blockchain = Blockchain()
    blockchain_three_blocks.chain[1] = 'evil_hash'

    with pytest.raises(Exception, match = 'The incoming chain is invalid'):
        blockchain.replace_chain(blockchain_three_blocks.chain)

def test_valid_transaction_chain(blockchain_three_blocks):
    Blockchain.is_valid_transaction_chain(blockchain_three_blocks.chain)
    
def test_is_valid_transaction_chain_duplicate_transactions(blockchain_three_blocks):
    transaction = Transaction(Wallet(), 'recipient', 1).to_json()

    blockchain_three_blocks.add_block([transaction, transaction])

    with pytest.raises(Exception, match ='is not unique'):
        Blockchain.is_valid_transaction_chain(blockchain_three_blocks.chain)

def test_is_valid_transaction_multiple_rewards(blockchain_three_blocks):
    reward_1 = Transaction.reward_transaction(Wallet()).to_json()
    reward_2 = Transaction.reward_transaction(Wallet()).to_json()

    blockchain_three_blocks.add_block([reward_1, reward_2])

    with pytest.raises(Exception, match ='one mining reward per block'):
        Blockchain.is_valid_transaction_chain(blockchain_three_blocks.chain)

def test_is_valid_transaction_chain_bad_Transaction(blockchain_three_blocks):
    bad_transaction = Transaction(Wallet(), 'recipient', 1)
    bad_transaction.input['signature'] = Wallet().sign(bad_transaction.output)
    blockchain_three_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception): #I'm not lookin for one Exception in particular
        Blockchain.is_valid_transaction_chain(blockchain_three_blocks.chain)

def test_is_valid_transaction_chain_bad_historic_balance(blockchain_three_blocks):
    wallet = Wallet()
    bad_transaction = Transaction(wallet, 'recipient', 1)
    bad_transaction.output[wallet.address] = 9000
    bad_transaction.input['amount'] = 9001
    bad_transaction.input['signature'] = wallet.sign(bad_transaction.output)

    blockchain_three_blocks.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception, match ='has an invalid input amount'):
        Blockchain.is_valid_transaction_chain(blockchain_three_blocks.chain)