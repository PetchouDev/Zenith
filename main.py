import os
import sys
import pathlib

from lib.crypto import get_token
from core.client import CLIENT


# get the path of the current file
PATH = pathlib.Path(__file__).parent.absolute()

# work in the parent directory
os.chdir(PATH)

# add an empty string to sys.argv to avoid a ListIndexError
sys.argv.append('')

# if the 'setup' argument is called, run the setup method, idem if the data/{token,password} file does not exist
if sys.argv[1] == 'setup' or not os.path.isfile('data/token') or not os.path.isfile('data/password'):
    from lib.setup import setup
    setup()
    sys.exit(0)

# if there is a need of a password, check if the password is correct
with open('data/password', 'r') as f:
    password_hash = f.read().strip()

token = get_token(password_hash)

CLIENT.wake_up(token)
