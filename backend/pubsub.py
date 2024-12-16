import time

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from backend.blockchain. block import Block
from backend.wallet.transaction import Transaction

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-2f936c54-8650-4414-9ec6-c917fb7ae97c'
pnconfig.publish_key = 'pub-c-00c59f9a-fb87-4045-b6ae-6f05ca575e13'


CHANNELS = { #creating a dictionary to contain all the created channels, whenever a need to create a channel I just add an entry here
    'TEST' : 'TEST', #Creating a channel for tests
    'BLOCK': 'BLOCK', #Creating a channel for the block
    'TRANSACTION' : 'TRANSACTION' #Creating a channel for the broadcast of the transactions
}


class Listener(SubscribeCallback): #creating a class that inherits the SubscribeCallback
    #By giving the Listener access to the blockchain I enable it to validate the incoming blocks
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool
    
    def message(self, pubnub, message_object):
        print(f'\n-- Channel: {message_object.channel} | Message: {message_object.message}')

        if message_object.channel == CHANNELS['BLOCK']:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:] #Creating a copy of the current chain, this chain is going to potentialy replace the current one
            potential_chain.append(block) #Now I have the current chain and the new Block added to it

            #The block that I will try to validate must be it's block version a not it's json representation
            try:
                self.blockchain.replace_chain(potential_chain) #Surround with try catch as it can go wrong
                self.transaction_pool.clear_blockchain_transaction(
                    self.blockchain
                )
                print('\n -- Successfullly replaced the local chain')
            except Exception as e:
                print(f'\n -- Did not replace chain: {e}') #e will show the actually exception raised

        elif message_object.channel == CHANNELS['TRANSACTION']:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print('\n -- Set the new transaction in the transaction pool')


class PubSub():
    """
    Handles the publish;subscribe layer of the application.
    Provides communication between the nodes of the blockchain network.
    """
    def __init__(self, blockchain, transaction_pool):        
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute() #this method takes a list of the channels that I want to subscribe to
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))
        
    def publish(self, channel, message):
        """
        Publish the message object to the channel.
        """
        self.pubnub.unsubscribe().channels([channel]).execute() #If this I avoid publishing a block and reading it myself which would cause an error
        self.pubnub.publish().channel(channel).message(message).sync() #takes a single channel that I want to subscribe to and the message that I want to send, sync is used to actually send the message
        self.pubnub.subscribe().channels([channel]).execute()

    def broadcast_block(self, block):
        """
        Broadcast a block object to all nodes.
        """
        #Remember that a PubNub message can only be broadcasted in basic formats

        self.publish(CHANNELS['BLOCK'], block.to_json()) #to_json will serialize the information so PubNub can handle it


    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction to all nodes.
        """
        self.publish(CHANNELS['TRANSACTION'], transaction.to_json())



def main():
    pubsub = PubSub()

    time.sleep(1) #with that I can guarantee that the subscribe will happen first than the publish
    
    pubsub.publish(CHANNELS['TEST'], {'foo' : 'bar'})

if __name__ == '__main__':
    main()