from backend.util.crypto_hash import crypto_hash

HEX_TO_BINARY_CONVERSION_TABLE = {
    '0':'0000',
    '1':'0001',
    '2':'0010',
    '3':'0011',
    '4':'0100',
    '5':'0101',
    '6':'0110',
    '7':'0111',
    '8':'1000',
    '9':'1001',
    'a':'1010',
    'b':'1011',
    'c':'1100',
    'd':'1101',
    'e':'1110',
    'f':'1111'
}

def hex_to_binary(hex_string):
    binary_string = '' #setting an empty string first

    for character in hex_string:
        binary_string += HEX_TO_BINARY_CONVERSION_TABLE[character]

    return binary_string

def main(): #exprimentational code
    number = 451
    hex_number = hex(number)[2:] #hex numbers starts with 0x so by starting from 2 I'm ignoring that specific part
    print(f'hex_number: {hex_number}')

    binary_number = hex_to_binary(hex_number)
    print(f'binary_number: {binary_number}')

    original_number = int(binary_number, 2) #converting a String into int, the 2 specifies that it's a binary String
    print(f'original_number: {original_number}')

    hex_to_binary_crypto_hash = hex_to_binary(crypto_hash('test-data'))    
    print(f'hex_to_binary_crypto_hash: {hex_to_binary_crypto_hash}')

if __name__ == '__main__':
    main()