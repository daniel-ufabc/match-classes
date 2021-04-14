import time
import redis

import config

redis_client = redis.Redis(host=config.REDIS_URL)
while True:
    try:
        redis_client.ping()
    except redis.exceptions.RedisError:
        time.sleep(2)
    else:
        break

# Now, redis server is up and running...
