import time

from backend.blockchain.blockchain import Blockchain
from backend.config import SECONDS

blockchain = Blockchain()

times = [] #list of the mine times

for i in range(1000):
    start_time = time.time_ns()
    blockchain.add_block(i)
    end_time = time.time_ns()

    time_to_mine = (end_time - start_time) / SECONDS #dividing to pass it to seconds
    times.append(time_to_mine)

    average_time = sum(times) / len(times)

    print(f'New Block difficulty: {blockchain.chain[-1].difficulty}') #getting the dfficulty from the last block in the chain
    print(f'Time to mine new block: {time_to_mine}s')
    print(f'Average time to add blocks: {average_time}s\n')