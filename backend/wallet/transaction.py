import time
import uuid

from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT

class Transaction:
    """
    Document of an exchange in currency from a sender to one 
    or more recipients.
    """
    def __init__(self,
                 sender_wallet = None,
                 recipient = None,
                 amount = None,
                 id = None,
                 output = None,
                 input = None #By giving a default value I won't get an error for not providing values
                 ):
        self.id = id or str(uuid.uuid4())[0:8] #will be useful for preventing duplicated transaction for example
        self.output = output or self.create_output(
            sender_wallet,
            recipient,
            amount
        )
        self.input = input or  self.create_input(sender_wallet, self.output) #if the input is not defined I use the second one 

    def create_output(self, sender_wallet, recipient, amount):
        """
        Structure the output data for the transaction.
        """
        if amount > sender_wallet.balance:
            raise Exception('Amount exceeds balance')

        output = {}
        output[recipient] = amount
        output[sender_wallet.address] = sender_wallet.balance - amount #The 'change' for the sender

        return output
    
    def create_input(self, sender_wallet, output):
            """
            Structure the unput data for the transaction.
            Sign the transaction and include the sender's public key and address
            """
            return{
                'timestamp': time.time_ns(),
                'amount': sender_wallet.balance,
                'address': sender_wallet.address,
                'public_key': sender_wallet.public_key,
                'signature': sender_wallet.sign(output)
            }   
    
    def update(self, sender_wallet, recipient, amount):
        """
        Update the transaction with an existing or new recipient.
        """
        if amount > self.output[sender_wallet.address]:
            raise Exception('Amount exceeds balance')
         
        if recipient in self.output:
            self.output[recipient] = self.output[recipient] + amount
        else:
            self.output[recipient] = amount

        self.output[sender_wallet.address] = \
            self.output[sender_wallet.address] - amount #the \ allows me to continue to have multiple lines of a single line of code
        
        self.input = self.create_input(sender_wallet, self.output)

    def to_json(self):
        """
        Seriralize the transaction.
        """
        return self.__dict__


    @staticmethod
    def from_json(transaction_json):
        """
        Desirazlise a transaction's json representation back into a 
        Transaction instance
        """
        return Transaction(**transaction_json) #consist of an id, input and output
        #I don't need to provide the rest as the values are none by default



    @staticmethod
    def is_valid_transaction(transaction):
        """
        Validate a transaction.
        Raise an exception for invalid transactions.
        """
        output_total = sum(transaction.output.values())

        if transaction.input == MINING_REWARD_INPUT: #if so the transaction is in fact a reward
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception('Invalid mining reward')
            return


        if transaction.input['amount'] != output_total:
            raise Exception('Invalid transaction output values')
        
        if not Wallet.verify(
            transaction.input['public_key'],
            transaction.output,
            transaction.input['signature']
        ):
            raise Exception('Invalid signature')
        
    @staticmethod
    def reward_transaction(miner_wallet):
        """
        Generate a reward transaction that award the miner.
        """
        output = {}
        output[miner_wallet.address] = MINING_REWARD

        return Transaction(input=MINING_REWARD_INPUT, output=output)
        
def main():
    transaction = Transaction(Wallet(), 'recipient', 15)
    print(f'transaction.__dict__: {transaction.__dict__}')

    transaction_json = transaction.to_json()
    restored_transaction = Transaction.from_json(transaction_json)
    print(f'restored_transaction.__dict__: {restored_transaction.__dict__}')


if __name__ == '__main__':
    main()
