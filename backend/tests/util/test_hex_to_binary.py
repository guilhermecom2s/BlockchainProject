from backend.util.hex_to_binary import hex_to_binary

def test_hex_to_binary():
    original_number = 789 #random number
    hex_number = hex(original_number)[2:] #ignoring the 0x at the beggining of the hex number
    binary_number = hex_to_binary(hex_number)

    assert int(binary_number, 2) == original_number #if I get the original number back the conversion is working properly