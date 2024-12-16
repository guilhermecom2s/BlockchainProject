import os
import requests
import random

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.blockchain.blockchain import Blockchain
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.wallet.transaction_pool import TransactionPool
from backend.pubsub import PubSub

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': 'http://localhost:3000'}}) #Using CORS for security, the r represents a regex string, and the /* is to match every endpoint
blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

@app.route('/') #I'm deffining and endpoint to my application, similar to to google.com/gmail for example
def route_default():
    return 'Welcome to the blockchain'

@app.route('/blockchain')
def route_blockchain():
    #return blockchain.__repr__() #without the __repr__ it won't work because the Flask doesn't support lists
    return jsonify(blockchain.to_json()) 

@app.route('/blockchain/range')
def route_blockchain_range():
    #the idea os this method is to allow the frontend to call for parts of the blockchain chain
    #http://localhost:5000/blockchain/range?start=2&end=5 this last parts as known as querry parameters, wi will use it now
    start = int(request.args.get('start')) #by default those values are strings
    end = int(request.args.get('end'))

    return jsonify(blockchain.to_json()[::-1][start:end]) #[::-1] will revert the order of the list, so the first block is actuallly the last, but most recent one

@app.route('/blockchain/length')
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

@app.route('/blockchain/mine')
def route_blockchain_mine():
    transaction_data = transaction_pool.transaction_data()
    transaction_data.append(Transaction.reward_transaction(wallet).to_json())
    blockchain.add_block(transaction_data) #transaction_data will give all the json representation of the transactions
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.clear_blockchain_transaction(blockchain)

    return jsonify(block.to_json())

@app.route('/wallet/transact', methods=['POST'])
def route_wallet_transact():
    transaction_data = request.get_json()
    transaction = transaction_pool.existing_transaction(wallet.address)
     
    if transaction:
        transaction.update(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )
    else:
        transaction = Transaction(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']
        )
     
    pubsub.broadcast_transaction(transaction)
    transaction_pool.set_transaction(transaction)
     
    return jsonify(transaction.to_json())

@app.route('/wallet/info')
def rout_wallet_info():
    return jsonify({'address': wallet.address, 'balance': wallet.balance})

@app.route('/known-addresses')
def route_known_addresses():
    know_addresses = set() #we only gonna set the addresses once

    for block in blockchain.chain:
        for transaction in block.data:
            know_addresses.update(transaction['output'].keys()) #taking all the recipients

    return jsonify(list(know_addresses))

@app.route('/transactions')
def route_transactions():
    return jsonify(transaction_pool.transaction_data())

ROOT_PORT = 5000
PORT = ROOT_PORT

if os.environ.get('PEER') == 'True': #Assigning a different port for every peer, I will assign True on the cmd
    PORT = random.randint(5001, 6000)

    #The requests is for a peer, that joins tha network later, to be able to get the latest block
    result = requests.get(f'http://localhost:{ROOT_PORT}/blockchain')
    result_blockchain = Blockchain.from_json(result.json())

    try:
        blockchain.replace_chain(result_blockchain.chain) #since it validates the chain it has a chance to raise an exception
        print('\n -- Successfully synchronized the local chain')
    except Exception as e:
        print(f'\n -- Error sychronizing: {e}')

if os.environ.get('SEED_DATA') == 'True': #Will compare the SEED_DATA with a given value in the environment
    for i in range(10):
        blockchain.add_block([
            Transaction(Wallet(), Wallet().address, random.randint(2,50)).to_json(),
            Transaction(Wallet(), Wallet().address, random.randint(2,50)).to_json()
        ])

    for i in range(3): #Making three transactions just for experimentations
        transaction_pool.set_transaction(
            Transaction(Wallet(), Wallet().address, random.randint(2,50))
        )

app.run(port = PORT) #The default port is 5000, but I can change if I want to deffining port = 

