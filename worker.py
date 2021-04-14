#!/usr/bin/env python
import sys
from rq import Connection, Worker
from redis import Redis
from config import REDIS_URL

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection(Redis(host=REDIS_URL)):
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
