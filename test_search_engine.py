# test_search_engine.py

from search_engine import handle_content, search
import redis

# Connect to Redis server
r = redis.Redis()

# Add some documents to the search engine
docs = [
    "Redis is a remote data structure server.",
    "You can think of it like memcached with strings, lists, sets, hashes, and sorted sets.",
    "Redis supports master/slave replication.",
    "Redis can be used as a database, cache, and message broker."
]

for i, doc in enumerate(docs):
    handle_content(r, "doc:", i, doc)

# Perform a search query
results, total = search(r, "doc:", "redis data", 0, 10)
print(f"Total documents found: {total}")
for doc_id, score in results:
    print(f"Document ID: {doc_id}, Score: {score}")
