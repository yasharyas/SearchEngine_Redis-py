# Redis Full-Text Search Implementation

## Overview

This project demonstrates a basic full-text search implementation using Redis. The code includes functionalities for adding content to an index, removing content from an index, and searching the index for specific terms. Redis Sorted Sets (`ZSETs`) are used to store term frequencies and compute relevance scores.

## Dependencies

- `redis` Python package
- Python standard libraries: `collections`, `re`, `os`, `math`

## Installation

1. Install the Redis server from the official [Redis website](https://redis.io/download).
2. Install the `redis` Python package using pip:
   ```sh
   pip install redis
   ```

## Code Structure

### Connecting to Redis

```python
import redis

r = redis.Redis()
```
Connects to the Redis server running on the default host (`localhost`) and port (`6379`).

### Basic Redis Commands

```python
r.sadd('temp1', '1')
r.sadd('temp2', '2')
print(r.sunion(['temp1', 'temp2']))
p = r.pipeline()
print(p.scard('temp1'))
p.scard('temp2')
print(p.execute())
r.zunionstore('temp3', {'temp1': 2, 'temp2': 3})
print(r.zrange('temp3', 0, -1, withscores=True))
```
Performs basic Redis operations to test the connection and command functionalities.

### Text Processing

```python
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
```
Processes text by removing non-word characters, converting to lowercase, and filtering out stop words. Computes term frequencies if `add` is `True`.

### Handling Content

```python
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
```
Adds or removes content from the Redis index. Uses pipelines for batch processing.

### Searching the Index

```python
def search(connection, prefix, query_string, offset=0, count=10):
    keys = [prefix + key for key in get_index_keys(query_string, False)]
    if not keys:
        return [], 0
    total_docs = max(connection.scard(prefix + 'indexed:'), 1)
    pipe = connection.pipeline(False)
    for key in keys:
        pipe.zcard(key)
    sizes = pipe.execute()
    def idf(count):
        if not count:
            return 0
        return max(math.log(total_docs / count, 2), 0)
    idfs = list(map(idf, sizes))
    weights = {key: idfv for key, size, idfv in zip(keys, sizes, idfs) if size}
    if not weights:
        return [], 0
    temp_key = prefix + 'temp:' + os.urandom(8).hex()
    try:
        known = connection.zunionstore(temp_key, weights)
        ids = connection.zrevrange(temp_key, offset, offset + count - 1, withscores=True)
    finally:
        connection.delete(temp_key)
    return ids, known
```
Searches the index for the query string, calculates term weights using IDF, and retrieves the most relevant documents.

## Usage

1. **Adding Content to the Index**:
   ```python
   handle_content(r, 'prefix:', 'doc1', 'This is a sample document.', add=True)
   ```

2. **Removing Content from the Index**:
   ```python
   handle_content(r, 'prefix:', 'doc1', 'This is a sample document.', add=False)
   ```

3. **Searching the Index**:
   ```python
   results, total = search(r, 'prefix:', 'sample search query')
   print(f"Total results: {total}")
   for doc_id, score in results:
       print(f"Document ID: {doc_id}, Score: {score}")
   ```

## License

This project is licensed under the MIT License.

---

