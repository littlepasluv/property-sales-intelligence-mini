import time
from functools import wraps
from typing import Dict, Any, Callable

_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}

def simple_cache(ttl: int = 60):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            now = time.time()
            
            if key in _cache and (now - _cache_timestamps.get(key, 0)) < ttl:
                return _cache[key]
            
            result = func(*args, **kwargs)
            _cache[key] = result
            _cache_timestamps[key] = now
            return result
        return wrapper
    return decorator

def clear_cache():
    _cache.clear()
    _cache_timestamps.clear()
