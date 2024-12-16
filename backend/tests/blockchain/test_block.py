import time
import pytest

from backend.blockchain.block import Block, GENESIS_DATA
from backend.util.hex_to_binary import hex_to_binary
from backend.config import MINE_RATE, SECONDS

def test_mine_block():
    last_block = Block.genesis()
    data = 'test-data'
    block = Block.mine_block(last_block, data)

    assert isinstance(block, Block)
    assert block.data == data
    assert block.last_hash == last_block.hash
    assert hex_to_binary(block.hash)[0:block.difficulty] == '0' * block.difficulty #asserting that the number of 0's in the pow is matched

def test_genesis():
    genesis = Block.genesis()

    assert isinstance(genesis, Block)

    #asserting that every element of the genesis data is correct
    for key, value in GENESIS_DATA.items():
        assert getattr(genesis, key) == value #getattr stands for get attribute

def test_quickly_mined_block():
    last_block = Block.mine_block(Block.genesis(), 'foo')
    mined_block = Block.mine_block(last_block, 'bar')

    assert mined_block.difficulty == last_block.difficulty + 1

def test_slowly_mined_block():
    last_block = Block.mine_block(Block.genesis(), 'foo')
    time.sleep(MINE_RATE / SECONDS) #waiting until it reaches the mine_rate so the difficulty can decrease
    mined_block = Block.mine_block(last_block, 'bar')

    assert mined_block.difficulty == last_block.difficulty - 1

def test_mined_block_difficulty_limits_at_1():
    last_block = Block(
        time.time_ns(),
        'test_last_hash',
        'test_hash',
        'test_data',
        1,
        0
    )

    time.sleep(MINE_RATE / SECONDS) #waiting until it reaches the mine_rate so the difficulty can decrease
    mined_block = Block.mine_block(last_block, 'bar')
    
    #it should decrease, but it can't, so I'm asserting it won't
    assert mined_block.difficulty == 1

@pytest.fixture #I can make a fixture that a lot of tests can share
def last_block():
    return Block.genesis()

@pytest.fixture
def block(last_block):
    return Block.mine_block(last_block, 'test_data')

def test_is_valid_block(last_block, block): 
    #in this test I won't use an assert, because I'm already using the exception, the test will pass implicity
    Block.is_valid_block(last_block, block)

def test_is_valid_block_bad_last_hash(last_block, block):
    block.last_hash = 'evil_last_hash'

    with pytest.raises(Exception, match='last_hash must be correct!'): #I'm expecting and Excpetion to be raised
        Block.is_valid_block(last_block, block)

def test_is_valid_bad_proof_of_work(last_block, block):
    block.hash = 'fff'

    with pytest.raises(Exception, match='The proof of work requirement was not met!'): #I'm expecting and Excpetion to be raised
        Block.is_valid_block(last_block, block)

def test_is_valid_block_jumped_difficulty(last_block, block):
    jumped_difficulty = 10 #just forcing a 'large' number
    block.difficulty = jumped_difficulty
    block.hash = f'{"0" * jumped_difficulty}111abc' #with this I'm manually validating the proof of work

    with pytest.raises(Exception, match='The block difficulty must only adjust by 1'): #I'm expecting and Excpetion to be raised
        Block.is_valid_block(last_block, block)

def test_is_valid_block_bad_block_hash(last_block, block):
    block.hash = '0000000000000000bbbabc' #theoretically it should pass the test, but I will check the hash validaty

    with pytest.raises(Exception, match='The block hash must be corret'): #I'm expecting and Excpetion to be raised
        Block.is_valid_block(last_block, block)