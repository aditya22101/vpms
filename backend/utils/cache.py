from extensions import redis_client, REDIS_AVAILABLE
import json

def get_cached(key):
    """Get value from cache"""
    if not REDIS_AVAILABLE or not redis_client:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None

def set_cached(key, value, timeout=300):
    """Set value in cache with timeout (seconds)"""
    if not REDIS_AVAILABLE or not redis_client:
        return False
    try:
        redis_client.setex(key, timeout, json.dumps(value))
        return True
    except Exception:
        return False

def delete_cached(key):
    """Delete value from cache"""
    if not REDIS_AVAILABLE or not redis_client:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False

def cache_response(timeout=300):
    """Decorator to cache API responses"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}_{str(kwargs)}"
            
            # Try to get from cache
            cached = get_cached(cache_key)
            if cached:
                return cached
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            set_cached(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

