import base64
import os
import sys


def log(msg: str):
    sys.stderr.write(msg + '\n')


def get_token():
    return base64.b64encode(os.urandom(64))[:80]
