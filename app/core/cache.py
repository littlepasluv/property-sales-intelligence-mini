import time
from functools import wraps
from typing import Dict, Any, Callable

# Simple in-memory cache with TTL
_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}

DEFAULT_TTL = 300  # 5 minutes

def generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """Generates a cache key from function name and arguments."""
    key = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
    return key

def get_from_cache(key: str) -> Any:
    """Retrieves an item from the cache if it's not expired."""
    if key in _cache and (time.time() - _cache_timestamps.get(key, 0)) < DEFAULT_TTL:
        return _cache[key]
    return None

def set_in_cache(key: str, value: Any):
    """Sets an item in the cache with the current timestamp."""
    _cache[key] = value
    _cache_timestamps[key] = time.time()

def clear_cache():
    """Clears the entire in-memory cache."""
    global _cache, _cache_timestamps
    _cache = {}
    _cache_timestamps = {}
    print("In-memory cache cleared.")

def simple_cache(ttl: int = DEFAULT_TTL):
    """
    A decorator for simple in-memory caching with a time-to-live (TTL).
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Exclude 'db' session from cache key
            kwargs_for_key = {k: v for k, v in kwargs.items() if k != 'db'}
            key = generate_cache_key(func.__name__, *args, **kwargs_for_key)
            
            cached_value = get_from_cache(key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            set_in_cache(key, result)
            return result
        return wrapper
    return decorator
