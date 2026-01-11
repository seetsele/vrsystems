"""
VERITY SYSTEMS - UPSTASH REDIS INTEGRATION
Rate limiting and caching with Upstash Redis for Python backend
"""

import os
import time
import json
import hashlib
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL = os.getenv('UPSTASH_REDIS_REST_URL', 'https://enabled-bat-54552.upstash.io')
UPSTASH_REDIS_REST_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN', '')


class UpstashRedis:
    """Upstash Redis REST API Client"""
    
    def __init__(self, url: str = None, token: str = None):
        self.url = url or UPSTASH_REDIS_REST_URL
        self.token = token or UPSTASH_REDIS_REST_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    async def command(self, *args) -> Any:
        """Execute a Redis command"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    headers=self.headers,
                    json=list(args),
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"Redis error: {response.status_code}")
                    return None
                
                data = response.json()
                return data.get('result')
                
        except Exception as e:
            print(f"Upstash Redis error: {e}")
            return None
    
    def command_sync(self, *args) -> Any:
        """Execute a Redis command synchronously"""
        try:
            response = httpx.post(
                self.url,
                headers=self.headers,
                json=list(args),
                timeout=10.0
            )
            
            if response.status_code != 200:
                print(f"Redis error: {response.status_code}")
                return None
            
            data = response.json()
            return data.get('result')
            
        except Exception as e:
            print(f"Upstash Redis error: {e}")
            return None
    
    # Basic operations
    async def get(self, key: str) -> Optional[str]:
        return await self.command('GET', key)
    
    async def set(self, key: str, value: str, ex: int = None, px: int = None, nx: bool = False) -> bool:
        args = ['SET', key, value]
        if ex:
            args.extend(['EX', ex])
        if px:
            args.extend(['PX', px])
        if nx:
            args.append('NX')
        return await self.command(*args)
    
    async def incr(self, key: str) -> int:
        return await self.command('INCR', key)
    
    async def incrby(self, key: str, amount: int) -> int:
        return await self.command('INCRBY', key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        return await self.command('EXPIRE', key, seconds)
    
    async def ttl(self, key: str) -> int:
        return await self.command('TTL', key)
    
    async def delete(self, key: str) -> int:
        return await self.command('DEL', key)
    
    # Sorted set operations
    async def zadd(self, key: str, score: float, member: str) -> int:
        return await self.command('ZADD', key, score, member)
    
    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        return await self.command('ZREMRANGEBYSCORE', key, min_score, max_score)
    
    async def zcard(self, key: str) -> int:
        return await self.command('ZCARD', key) or 0
    
    async def zrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        if withscores:
            return await self.command('ZRANGE', key, start, stop, 'WITHSCORES')
        return await self.command('ZRANGE', key, start, stop)
    
    # Hash operations
    async def hset(self, key: str, field: str, value: str) -> int:
        return await self.command('HSET', key, field, value)
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        return await self.command('HGET', key, field)
    
    async def hgetall(self, key: str) -> Dict:
        result = await self.command('HGETALL', key)
        if not result:
            return {}
        # Convert alternating list to dict
        return {result[i]: result[i + 1] for i in range(0, len(result), 2)}
    
    async def hincrby(self, key: str, field: str, amount: int) -> int:
        return await self.command('HINCRBY', key, field, amount)


class VerityRateLimiter:
    """Rate limiter using sliding window algorithm"""
    
    # Rate limits by plan type (requests per minute)
    LIMITS = {
        'pay_per_use': 60,
        'api_starter': 60,
        'api_developer': 120,
        'api_pro': 240,
        'api_business': 600,
        'api_enterprise': 10000,
        'free': 10
    }
    
    def __init__(self, redis: UpstashRedis):
        self.redis = redis
    
    async def check_limit(self, user_id: str, plan_type: str = 'free') -> Dict[str, Any]:
        """Check if request is allowed under rate limit"""
        limit = self.LIMITS.get(plan_type, self.LIMITS['free'])
        window = 60  # 1 minute window
        now = int(time.time() * 1000)
        window_start = now - (window * 1000)
        key = f"rate_limit:{user_id}"
        
        try:
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await self.redis.zcard(key)
            
            if current_count >= limit:
                # Get reset time
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest and len(oldest) >= 2:
                    reset_time = int((float(oldest[1]) + (window * 1000)) / 1000)
                else:
                    reset_time = int((now + (window * 1000)) / 1000)
                
                return {
                    'allowed': False,
                    'limit': limit,
                    'remaining': 0,
                    'reset': reset_time,
                    'retry_after': max(1, reset_time - int(now / 1000))
                }
            
            # Add current request
            import random
            await self.redis.zadd(key, now, f"{now}-{random.random()}")
            await self.redis.expire(key, window + 10)
            
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - current_count - 1,
                'reset': int((now + (window * 1000)) / 1000)
            }
            
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - 1,
                'reset': int((now + (window * 1000)) / 1000),
                'error': str(e)
            }
    
    async def check_daily_limit(self, user_id: str, daily_limit: int = 10000) -> Dict[str, Any]:
        """Check daily API usage limit"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"daily_limit:{user_id}:{today}"
        
        try:
            current = await self.redis.get(key)
            current = int(current) if current else 0
            
            if current >= daily_limit:
                return {
                    'allowed': False,
                    'limit': daily_limit,
                    'used': current,
                    'remaining': 0
                }
            
            await self.redis.incr(key)
            await self.redis.expire(key, 86400 + 3600)  # 25 hours
            
            return {
                'allowed': True,
                'limit': daily_limit,
                'used': current + 1,
                'remaining': daily_limit - current - 1
            }
            
        except Exception as e:
            print(f"Daily limit check error: {e}")
            return {'allowed': True, 'limit': daily_limit, 'used': 0, 'remaining': daily_limit}


class VerityUsageTracker:
    """Track API usage for billing"""
    
    # Pricing in cents
    PRICING = {
        'standard': 6,      # $0.06
        'premium': 10,      # $0.10
        'bulk': 5,          # $0.05
        'verify_plus': 150  # $1.50
    }
    
    # Volume discounts
    VOLUME_DISCOUNTS = [
        (100000, 0.40),  # 40% discount for 100K+
        (25000, 0.30),   # 30% discount for 25K+
        (5000, 0.20),    # 20% discount for 5K+
        (1000, 0.10),    # 10% discount for 1K+
        (0, 0.00)        # No discount
    ]
    
    def __init__(self, redis: UpstashRedis):
        self.redis = redis
    
    def get_volume_discount(self, count: int) -> float:
        """Get volume discount percentage based on monthly usage"""
        for threshold, discount in self.VOLUME_DISCOUNTS:
            if count >= threshold:
                return discount
        return 0.0
    
    async def track_usage(self, user_id: str, verification_type: str = 'standard') -> Dict[str, Any]:
        """Track a verification request"""
        now = datetime.now()
        month_key = f"usage:{user_id}:{now.strftime('%Y-%m')}"
        day_key = f"usage:{user_id}:{now.strftime('%Y-%m-%d')}"
        
        # Get base cost
        cost_cents = self.PRICING.get(verification_type, self.PRICING['standard'])
        
        try:
            # Get current count for volume discount
            current_data = await self.redis.hgetall(month_key)
            current_count = int(current_data.get('total_count', 0))
            
            # Apply volume discount
            discount = self.get_volume_discount(current_count)
            discounted_cost = int(cost_cents * (1 - discount))
            
            # Increment monthly counters
            await self.redis.hincrby(month_key, 'total_count', 1)
            await self.redis.hincrby(month_key, f'{verification_type}_count', 1)
            await self.redis.hincrby(month_key, 'total_cost_cents', discounted_cost)
            await self.redis.expire(month_key, 86400 * 35)  # 35 days
            
            # Increment daily counter
            await self.redis.incr(day_key)
            await self.redis.expire(day_key, 86400 * 2)
            
            return {
                'success': True,
                'cost_cents': discounted_cost,
                'discount_applied': discount,
                'new_count': current_count + 1
            }
            
        except Exception as e:
            print(f"Usage tracking error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_monthly_usage(self, user_id: str) -> Dict[str, Any]:
        """Get usage for current month"""
        now = datetime.now()
        month_key = f"usage:{user_id}:{now.strftime('%Y-%m')}"
        
        try:
            data = await self.redis.hgetall(month_key)
            
            total_count = int(data.get('total_count', 0))
            
            return {
                'total_count': total_count,
                'standard_count': int(data.get('standard_count', 0)),
                'premium_count': int(data.get('premium_count', 0)),
                'bulk_count': int(data.get('bulk_count', 0)),
                'verify_plus_count': int(data.get('verify_plus_count', 0)),
                'total_cost_cents': int(data.get('total_cost_cents', 0)),
                'total_cost': int(data.get('total_cost_cents', 0)) / 100,
                'current_discount': self.get_volume_discount(total_count)
            }
            
        except Exception as e:
            print(f"Get usage error: {e}")
            return {'total_count': 0, 'total_cost': 0}
    
    async def get_daily_usage(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily usage for charts"""
        usage = []
        now = datetime.now()
        
        for i in range(days):
            date = now - timedelta(days=i)
            day_key = f"usage:{user_id}:{date.strftime('%Y-%m-%d')}"
            
            try:
                count = await self.redis.get(day_key)
                usage.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': int(count) if count else 0
                })
            except:
                usage.append({'date': date.strftime('%Y-%m-%d'), 'count': 0})
        
        return list(reversed(usage))


class VerityCache:
    """Caching layer for API responses and sessions"""
    
    def __init__(self, redis: UpstashRedis):
        self.redis = redis
    
    async def cache_api_key(self, key_hash: str, user_data: Dict, ttl: int = 300) -> bool:
        """Cache API key validation result"""
        key = f"api_key:{key_hash}"
        try:
            await self.redis.set(key, json.dumps(user_data), ex=ttl)
            return True
        except Exception as e:
            print(f"Cache API key error: {e}")
            return False
    
    async def get_cached_api_key(self, key_hash: str) -> Optional[Dict]:
        """Get cached API key data"""
        key = f"api_key:{key_hash}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Get cached API key error: {e}")
            return None
    
    async def invalidate_api_key(self, key_hash: str) -> bool:
        """Invalidate API key cache"""
        key = f"api_key:{key_hash}"
        try:
            await self.redis.delete(key)
            return True
        except:
            return False
    
    async def cache_verification(self, claim_hash: str, result: Dict, ttl: int = 3600) -> bool:
        """Cache verification result"""
        key = f"verification:{claim_hash}"
        try:
            await self.redis.set(key, json.dumps(result), ex=ttl)
            return True
        except:
            return False
    
    async def get_cached_verification(self, claim_hash: str) -> Optional[Dict]:
        """Get cached verification"""
        key = f"verification:{claim_hash}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except:
            return None


def hash_claim(claim: str) -> str:
    """Generate hash for a claim to use as cache key"""
    normalized = claim.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def hash_api_key(api_key: str) -> str:
    """Generate hash for API key"""
    return hashlib.sha256(api_key.encode()).hexdigest()[:32]


# Initialize global instances
redis_client = UpstashRedis()
rate_limiter = VerityRateLimiter(redis_client)
usage_tracker = VerityUsageTracker(redis_client)
cache = VerityCache(redis_client)


# Middleware function for FastAPI
async def rate_limit_middleware(user_id: str, plan_type: str = 'free'):
    """Rate limiting middleware for API routes"""
    result = await rate_limiter.check_limit(user_id, plan_type)
    
    if not result['allowed']:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'Rate limit exceeded',
                'limit': result['limit'],
                'retry_after': result['retry_after']
            },
            headers={
                'X-RateLimit-Limit': str(result['limit']),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(result['reset']),
                'Retry-After': str(result['retry_after'])
            }
        )
    
    return result


# Usage tracking decorator
def track_api_usage(verification_type: str = 'standard'):
    """Decorator to track API usage"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get user_id from kwargs or request
            user_id = kwargs.get('user_id') or 'anonymous'
            
            # Track usage
            await usage_tracker.track_usage(user_id, verification_type)
            
            # Execute the function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


print("✅ Upstash Redis Python integration loaded")
