import redis
import time
from functools import wraps
from fastapi import Request, HTTPException

class RateLimiter:
    """Advanced Redis-backed Rate Limiter"""
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.enabled = True
        except:
            self.enabled = False
            print("Redis not found. Rate limiting disabled.")

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        if not self.enabled: return True
        
        current_time = int(time.time())
        window_key = f"rl:{key}:{current_time // window}"
        
        count = self.redis.incr(window_key)
        if count == 1:
            self.redis.expire(window_key, window * 2)
            
        return count <= limit

# Basic local implementation if Redis is missing
class LocalLimiter:
    def __init__(self):
        self.history = {}
        
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        if key not in self.history:
            self.history[key] = []
        
        # Clean old entries
        self.history[key] = [t for t in self.history[key] if now - t < window]
        
        if len(self.history[key]) >= limit:
            return False
        
        self.history[key].append(now)
        return True
