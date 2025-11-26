import redis

# Redis client with error handling
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.TimeoutError, Exception):
    REDIS_AVAILABLE = False
    redis_client = None
    print("Warning: Redis is not available. Caching will be disabled.")

