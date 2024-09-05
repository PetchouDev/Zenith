import sys
import hashlib


def hash_string(string):
    for _ in range(10000):
        string = hashlib.sha256(string.encode()).hexdigest()

    return string

def get_token(password_hash):
    if password_hash == "NOPASS":
        with open('data/token', 'r') as f:
            return f.read().strip()

    # try to get the password from the arguments
    password = sys.argv[1]

    if password_hash != hash_string(password) or password == '':
        print("Invalid or not provided password from command line")
        print("Please enter the password:")
        password = input()
        print(password, password_hash)
        if password_hash != hash_string(password):
            print("Invalid password")
            sys.exit(1)
    
    print("Password correct")
    with open('data/token', 'rb') as f:
        token = f.read()
        return xor_bytes(token, password.encode()).decode()
    
def xor_bytes(b1, b2):
    # make sure the key is at least as long as the bytes
    while len(b2) < len(b1):
        b2 += b2
    # xor the bytes
    return bytes([a ^ b for a, b in zip(b1, b2)])



