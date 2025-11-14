"""
Cache decorators for API views
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
import hashlib
import json


def cache_api_response(cache_key_prefix, timeout=None):
    """
    Decorator to cache API responses
    
    Args:
        cache_key_prefix: Prefix for the cache key
        timeout: Cache timeout in seconds (uses settings.CACHE_TTL if not provided)
    
    Usage:
        @cache_api_response('occupation_summary', timeout=300)
        def summary(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Build cache key from prefix, query params, and user
            query_params = dict(request.query_params)
            cache_key_data = {
                'prefix': cache_key_prefix,
                'params': query_params,
                'user': str(request.user.id) if request.user.is_authenticated else 'anonymous',
                'args': args,
                'kwargs': {k: v for k, v in kwargs.items() if k != 'pk'}
            }
            
            # Generate unique cache key
            cache_key_string = json.dumps(cache_key_data, sort_keys=True)
            cache_key_hash = hashlib.md5(cache_key_string.encode()).hexdigest()
            cache_key = f"{cache_key_prefix}:{cache_key_hash}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                # Add cache hit header for debugging
                response = Response(cached_response)
                response['X-Cache'] = 'HIT'
                return response
            
            # Execute the view function
            response = func(self, request, *args, **kwargs)
            
            # Cache the response data
            if response.status_code == 200 and hasattr(response, 'data'):
                # Determine timeout
                ttl = timeout
                if ttl is None:
                    ttl = settings.CACHE_TTL.get(cache_key_prefix, 300)
                
                cache.set(cache_key, response.data, ttl)
                
                # Add cache miss header for debugging
                response['X-Cache'] = 'MISS'
            
            return response
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern
    
    Args:
        pattern: Cache key pattern to match (e.g., 'occupation_*')
    
    Usage:
        invalidate_cache_pattern('occupation_*')
    """
    try:
        # Get all keys matching pattern
        cache_client = cache.client.get_client()
        keys = cache_client.keys(f"sigeti_bi:*{pattern}*")
        
        if keys:
            # Delete all matching keys
            cache_client.delete(*keys)
            return len(keys)
    except Exception as e:
        print(f"Error invalidating cache pattern {pattern}: {e}")
    
    return 0


def clear_related_caches(*cache_prefixes):
    """
    Decorator to clear related caches after a write operation
    
    Args:
        *cache_prefixes: Cache key prefixes to invalidate
    
    Usage:
        @clear_related_caches('occupation_summary', 'occupation_zones')
        def perform_create(self, serializer):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function
            result = func(*args, **kwargs)
            
            # Invalidate related caches
            for prefix in cache_prefixes:
                invalidate_cache_pattern(prefix)
            
            return result
        
        return wrapper
    return decorator
