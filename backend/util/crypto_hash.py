import hashlib
import json

def crypto_hash(*args): #*args will be a list of all the arguments that I pass into crypto_hash
    """
    Return a sha-256 hash of the given arguments.
    """
    stringified_data = sorted(map(lambda data: json.dumps(data), args))   #the map function takes a function and a list as parameters, the list will be transformed
    #in that way a stringify every element of the args list, not the list itself
    #json.dumps dumps the original data into a string representation
    #the lambda function is a simple way to declare function in python
    #the sorted will assure that with the same inputs, no matter the other I'll get the same output, maybe I'll remove it latter

    joined_data = ''.join(stringified_data)

    return hashlib.sha256(joined_data.encode('utf-8')).hexdigest() #The encode transforms the original string in its byte representation

def main():
    print(f"crypto_hash('one', 2, [3]): {crypto_hash('one', 2, [3])}")

if __name__ == '__main__':
    main()