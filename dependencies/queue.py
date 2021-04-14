from rq import Queue
from .redis import redis_client

redis_queue = Queue(connection=redis_client)