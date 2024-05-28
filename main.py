import redis
import collections
import re
import os
import math

# Connect to Redis
r = redis.Redis()

# Test Redis connection and basic commands
r.sadd('temp1', '1')
r.sadd('temp2', '2')
print(r.sunion(['temp1', 'temp2']))
p = r.pipeline()
print(p.scard('temp1'))
p.scard('temp2')
print(p.execute())
r.zunionstore('temp3', {'temp1': 2, 'temp2': 3})
print(r.zrange('temp3', 0, -1, withscores=True))
