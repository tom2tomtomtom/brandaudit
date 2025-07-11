"""
Intelligent Caching Service for Brand Audit App
Multi-layer caching with smart invalidation and performance optimization
"""

import json
import hashlib
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from functools import wraps
import pickle
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.extensions import cache as flask_cache


class IntelligentCacheService:
    """
    Multi-layer caching service with intelligent invalidation strategies
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        }
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            try:
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                self.redis_client.ping()
                self.logger.info("Redis cache initialized successfully")
            except Exception as e:
                self.logger.warning(f"Redis not available, using local cache only: {str(e)}")
                self.redis_client = None
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            'api_response': 3600,      # 1 hour for API responses
            'analysis_result': 86400,  # 24 hours for analysis results
            'brand_info': 7200,        # 2 hours for brand information
            'image_metadata': 43200,   # 12 hours for image metadata
            'news_data': 1800,         # 30 minutes for news data
            'visual_analysis': 21600,  # 6 hours for visual analysis
            'llm_response': 7200       # 2 hours for LLM responses
        }
    
    async def get(self, key: str, cache_type: str = 'default') -> Optional[Any]:
        """
        Get value from cache with multi-layer fallback
        """
        try:
            # Try Redis first (if available)
            if self.redis_client:
                try:
                    cached_data = self.redis_client.get(key)
                    if cached_data:
                        self.cache_stats['hits'] += 1
                        return pickle.loads(cached_data)
                except Exception as e:
                    self.logger.warning(f"Redis get failed: {str(e)}")
            
            # Fallback to local cache
            if key in self.local_cache:
                cache_entry = self.local_cache[key]
                if not self._is_expired(cache_entry):
                    self.cache_stats['hits'] += 1
                    return cache_entry['data']
                else:
                    # Remove expired entry
                    del self.local_cache[key]
            
            # Try Flask cache as final fallback
            try:
                cached_value = flask_cache.get(key)
                if cached_value is not None:
                    self.cache_stats['hits'] += 1
                    return cached_value
            except Exception as e:
                self.logger.warning(f"Flask cache get failed: {str(e)}")
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {str(e)}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, cache_type: str = 'default', ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with intelligent TTL
        """
        try:
            # Determine TTL
            if ttl is None:
                ttl = self.ttl_settings.get(cache_type, 3600)
            
            # Store in Redis (if available)
            if self.redis_client:
                try:
                    serialized_data = pickle.dumps(value)
                    self.redis_client.setex(key, ttl, serialized_data)
                except Exception as e:
                    self.logger.warning(f"Redis set failed: {str(e)}")
            
            # Store in local cache
            expiry_time = datetime.utcnow() + timedelta(seconds=ttl)
            self.local_cache[key] = {
                'data': value,
                'expiry': expiry_time,
                'cache_type': cache_type
            }
            
            # Store in Flask cache
            try:
                flask_cache.set(key, value, timeout=ttl)
            except Exception as e:
                self.logger.warning(f"Flask cache set failed: {str(e)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {str(e)}")
            return False
    
    async def invalidate(self, pattern: str = None, cache_type: str = None) -> int:
        """
        Intelligent cache invalidation
        """
        invalidated_count = 0
        
        try:
            # Redis invalidation
            if self.redis_client and pattern:
                try:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        invalidated_count += self.redis_client.delete(*keys)
                except Exception as e:
                    self.logger.warning(f"Redis invalidation failed: {str(e)}")
            
            # Local cache invalidation
            keys_to_remove = []
            for key, cache_entry in self.local_cache.items():
                should_invalidate = False
                
                if pattern and pattern in key:
                    should_invalidate = True
                elif cache_type and cache_entry.get('cache_type') == cache_type:
                    should_invalidate = True
                
                if should_invalidate:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.local_cache[key]
                invalidated_count += 1
            
            # Flask cache invalidation (clear all if pattern matching not available)
            if pattern or cache_type:
                try:
                    flask_cache.clear()
                except Exception as e:
                    self.logger.warning(f"Flask cache clear failed: {str(e)}")
            
            self.cache_stats['invalidations'] += invalidated_count
            self.logger.info(f"Invalidated {invalidated_count} cache entries")
            
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Cache invalidation failed: {str(e)}")
            return 0
    
    def cache_analysis_result(self, ttl: int = None):
        """
        Decorator for caching analysis results
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key, 'analysis_result')
                if cached_result is not None:
                    self.logger.info(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                if result and not result.get('error'):
                    await self.set(cache_key, result, 'analysis_result', ttl)
                    self.logger.info(f"Cached result for {func.__name__}")
                
                return result
            
            return wrapper
        return decorator
    
    def cache_api_response(self, ttl: int = None):
        """
        Decorator for caching API responses
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                cached_result = await self.get(cache_key, 'api_response')
                if cached_result is not None:
                    return cached_result
                
                result = await func(*args, **kwargs)
                if result and result.get('success'):
                    await self.set(cache_key, result, 'api_response', ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generate deterministic cache key from function signature
        """
        try:
            # Create a deterministic representation of arguments
            key_data = {
                'function': func_name,
                'args': str(args),
                'kwargs': sorted(kwargs.items()) if kwargs else []
            }
            
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"
            
        except Exception as e:
            # Fallback to simple key
            self.logger.warning(f"Cache key generation failed: {str(e)}")
            return f"cache:{func_name}:{hash(str(args) + str(kwargs))}"
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """
        Check if cache entry is expired
        """
        return datetime.utcnow() > cache_entry.get('expiry', datetime.utcnow())
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        """
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate_percentage': round(hit_rate, 2),
            'invalidations': self.cache_stats['invalidations'],
            'local_cache_size': len(self.local_cache),
            'redis_available': self.redis_client is not None
        }
        
        # Add Redis stats if available
        if self.redis_client:
            try:
                redis_info = self.redis_client.info('memory')
                stats['redis_memory_usage'] = redis_info.get('used_memory_human', 'Unknown')
                stats['redis_keys'] = self.redis_client.dbsize()
            except Exception as e:
                self.logger.warning(f"Failed to get Redis stats: {str(e)}")
        
        return stats
    
    async def cleanup_expired_entries(self) -> int:
        """
        Clean up expired entries from local cache
        """
        expired_keys = []
        current_time = datetime.utcnow()
        
        for key, cache_entry in self.local_cache.items():
            if current_time > cache_entry.get('expiry', current_time):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


# Global instance
intelligent_cache = IntelligentCacheService()
