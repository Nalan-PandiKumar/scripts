import sys

def check_isvalid_binary(binary_num):

    """
        This function checks whether a given string is a valid binary number.
        
        A valid binary string consists only of the characters '0' and '1', and 
        must be non-empty.

        Functionality:
        1. Receives a string as input.
        2. Checks if the string contains only '0's and '1's.
        3. Returns True if valid, False otherwise.

        Example usage:
        input: '101010'
        output: True
        
        input: '10201'
        output: False
        
        :param binary_str: The string to validate as a binary number.
        :return: True if the string is a valid binary number, otherwise False.
    """
    # Check if the string is non-empty and contains only '0' or '1'
    return all(char in '01' for char in binary_num)
    
    
    
def format_binary(binary_num):
    """
        This function formats a binary number string by splitting it into chunks of 8 bits (1 byte), 
        adding spaces between each chunk. It also adds preceding zeros to ensure the total number of 
        bits is a multiple of 8.

        Functionality:
        1. Receives a binary string as input (e.g., '111111111').
        2. Adds preceding zeros to make the total length a multiple of 8 bits.
            - Example: '111111111' becomes '00000001 11111111'.
        3. Splits the padded binary string into chunks of 8 bits (1 byte), separating them with spaces.
        4. Returns the formatted binary string.

        Example usage:
        input: '111111111'
        output: '00000001 11111111'
        
        :param binary_str: The binary number string to format.
        :return: A formatted string of the binary number split into 8-bit chunks with padding.
    """
    length = len(binary_num)
    #Padding zeros to make the total  length a multiple of 8 bits.
    padding_length = ( 8 - (length % 8) )% 8

    #Adds preceding zeros to make the total length a multiple of 8 bits.
    padded_binary = ('0' * padding_length) + binary_num


    #Splits the padded binary string into chunks of 8 bits (1 byte), separating them with spaces.
    format_padded_binary = ' '.join(list(padded_binary[i:i+8] for i in range(0,len(padded_binary),8)))

    #Returns the formatted binary string.
    return  format_padded_binary,(length + padding_length) // 8



if(len(sys.argv) > 1):
    binary_num = sys.argv[1]
    #Validating the input
    assert(check_isvalid_binary(binary_num)),"\x1b[0;31m <ERROR> :Invalid Binary\x1b[0m\n"
    
    formated_binary,size = format_binary(binary_num)
    print(f"0b:\x1b[0;32m{formated_binary}\x1b[0m | size:\x1b[0;31m{size}-{'Bytes' if(size>1) else 'Byte':}\x1b[0m")
else:
    assert 0, "\x1b[0;31m <ERROR> :The process excepts command line arguments\x1b[0m\n"

