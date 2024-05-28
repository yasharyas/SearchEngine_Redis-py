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

NON_WORDS = re.compile("[^a-z0-9' ]")
STOP_WORDS = set('''a able about across after all almost also am among an and any are as at be because been but by can cannot could dear did do does either else ever every for from get got had has have he her hers him his how however i if in into is it its just least let like likely may me might most must my neither no nor not of off often on only or other our own rather said say says she should since so some than that the their them then there these they this tis to too twas us wants was we were what when where which while who whom why will with would yet you your'''.split())

def get_index_keys(content, add=True):
    words = NON_WORDS.sub(' ', content.lower()).split()
    words = [word.strip("'") for word in words]
    words = [word for word in words if word not in STOP_WORDS and len(word) > 1]
    if not add:
        return words
    counts = collections.defaultdict(float)
    for word in words:
        counts[word] += 1
    wordcount = len(words)
    tf = dict((word, count / wordcount) for word, count in counts.items())
    return tf

def handle_content(connection, prefix, id, content, add=True):
    keys = get_index_keys(content)
    pipe = connection.pipeline(False)
    if add:
        pipe.sadd(prefix + 'indexed:', id)
        for key, value in keys.items():
            pipe.zadd(prefix + key, {id: value})
    else:
        pipe.srem(prefix + 'indexed:', id)
        for key in keys:
            pipe.zrem(prefix + key, id)
    pipe.execute()
    return len(keys)

def handle_content(connection, prefix, doc_id, content, add=True):
    keys = get_index_keys(content)

    pipe = connection.pipeline(False)

    if add:
        pipe.sadd(prefix + 'indexed:', doc_id)
        for key, value in keys.items():
            pipe.zadd(prefix + key, {doc_id: value})
    else:
        pipe.srem(prefix + 'indexed:', doc_id)
        for key in keys:
            pipe.zrem(prefix + key, doc_id)

    pipe.execute()
    return len(keys)
