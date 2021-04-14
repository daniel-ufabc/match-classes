import os
import hashlib
import time
from datetime import datetime as dt
import base64

import config


def data_filename(basename):
    return os.path.join(config.ABSOLUTE_DATA_SUBDIR, basename.strip())


def upload_filename(basename):
    return os.path.join(config.ABSOLUTE_DATA_SUBDIR, basename.strip())


def t_stamp():
    ts = time.time()
    return dt.fromtimestamp(ts).strftime('%Y%m%d%H%M%S') + f'.{ts:.6f}'.split('.')[-1]


def get_hash(data):
    return base64.urlsafe_b64encode(hashlib.sha1(data.encode("utf-8")).digest()).decode('utf-8')


def generate_upload_basename(data, filename='', extension=''):
    return t_stamp() + '.' + get_hash(data + t_stamp() + (filename or data)) + extension
