from .crypto import hash_string, xor_bytes


def setup():
    print("Welcome to the setup wizard!")
    print("Please your bot's token:")
    token = input()
    print("Should the token be encoded by a password? (y/n, default: y)")
    choice = input()
    if choice.lower().startswith('n'):
        # write NOPASS into data/password
        with open('data/password', 'w') as f:
            f.write('NOPASS')
        # write the token into data/token
        with open('data/token', 'w') as f:
            f.write(token)
    else:
        print("Please enter a password:")
        password = input()
        if password == '':
            print("Password cannot be empty, choose not to use one if you don't want to use a password.")
            return
        # write the password into data/password
        with open('data/password', 'w') as f:
            f.write(hash_string(password))
        # write the encoded token into data/token
        with open('data/token', 'wb') as f:
            f.write(xor_bytes(token.encode(), password.encode()))

    print("Setup complete! Please run the bot again to start it. You can pass the password as the first argument to the bot to skip the setup.")