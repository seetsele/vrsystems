// ================================================
// VERITY SYSTEMS - UPSTASH REDIS CLIENT
// Rate limiting and caching with Upstash Redis
// ================================================

// Upstash Redis Configuration
// Get these from https://console.upstash.com/
const UPSTASH_REDIS_REST_URL = process.env.UPSTASH_REDIS_REST_URL || 'https://enabled-bat-54552.upstash.io';
const UPSTASH_REDIS_REST_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || 'YOUR_UPSTASH_TOKEN';

/**
 * Upstash Redis Client for Verity Systems
 * Uses REST API for serverless compatibility
 */
class UpstashRedis {
    constructor(url = UPSTASH_REDIS_REST_URL, token = UPSTASH_REDIS_REST_TOKEN) {
        this.url = url;
        this.token = token;
    }

    /**
     * Execute a Redis command via REST API
     */
    async command(cmd, ...args) {
        try {
            const response = await fetch(`${this.url}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([cmd, ...args])
            });

            if (!response.ok) {
                throw new Error(`Redis error: ${response.status}`);
            }

            const data = await response.json();
            return data.result;
        } catch (error) {
            console.error('Upstash Redis error:', error);
            return null;
        }
    }

    // Basic operations
    async get(key) {
        return this.command('GET', key);
    }

    async set(key, value, options = {}) {
        const args = [key, value];
        if (options.ex) args.push('EX', options.ex);
        if (options.px) args.push('PX', options.px);
        if (options.nx) args.push('NX');
        if (options.xx) args.push('XX');
        return this.command('SET', ...args);
    }

    async incr(key) {
        return this.command('INCR', key);
    }

    async incrBy(key, amount) {
        return this.command('INCRBY', key, amount);
    }

    async expire(key, seconds) {
        return this.command('EXPIRE', key, seconds);
    }

    async ttl(key) {
        return this.command('TTL', key);
    }

    async del(key) {
        return this.command('DEL', key);
    }

    // Sorted set operations for sliding window rate limiting
    async zadd(key, score, member) {
        return this.command('ZADD', key, score, member);
    }

    async zremrangebyscore(key, min, max) {
        return this.command('ZREMRANGEBYSCORE', key, min, max);
    }

    async zcard(key) {
        return this.command('ZCARD', key);
    }

    async zrange(key, start, stop, withScores = false) {
        if (withScores) {
            return this.command('ZRANGE', key, start, stop, 'WITHSCORES');
        }
        return this.command('ZRANGE', key, start, stop);
    }

    // Hash operations
    async hset(key, field, value) {
        return this.command('HSET', key, field, value);
    }

    async hget(key, field) {
        return this.command('HGET', key, field);
    }

    async hgetall(key) {
        return this.command('HGETALL', key);
    }

    async hincrby(key, field, amount) {
        return this.command('HINCRBY', key, field, amount);
    }
}

/**
 * Rate Limiter using Upstash Redis
 * Implements sliding window algorithm
 */
class VerityRateLimiter {
    constructor(redis) {
        this.redis = redis;
        
        // Rate limits by plan type (requests per minute)
        this.limits = {
            'pay_per_use': 60,
            'api_starter': 60,
            'api_developer': 120,
            'api_pro': 240,
            'api_business': 600,
            'api_enterprise': 10000, // Effectively unlimited
            'free': 10  // Free tier
        };
    }

    /**
     * Check if request is allowed under rate limit
     * Uses sliding window algorithm
     */
    async checkLimit(userId, planType = 'free') {
        const limit = this.limits[planType] || this.limits['free'];
        const window = 60; // 1 minute window in seconds
        const now = Date.now();
        const windowStart = now - (window * 1000);
        const key = `rate_limit:${userId}`;

        try {
            // Remove old entries outside the window
            await this.redis.zremrangebyscore(key, 0, windowStart);

            // Count current requests in window
            const currentCount = await this.redis.zcard(key) || 0;

            if (currentCount >= limit) {
                // Get oldest entry for reset time
                const oldest = await this.redis.zrange(key, 0, 0, true);
                const resetTime = oldest && oldest.length >= 2 
                    ? Math.ceil((parseFloat(oldest[1]) + (window * 1000)) / 1000)
                    : Math.ceil((now + (window * 1000)) / 1000);

                return {
                    allowed: false,
                    limit,
                    remaining: 0,
                    reset: resetTime,
                    retryAfter: Math.max(1, resetTime - Math.floor(now / 1000))
                };
            }

            // Add current request
            await this.redis.zadd(key, now, `${now}-${Math.random()}`);
            await this.redis.expire(key, window + 10); // Extra 10 seconds buffer

            return {
                allowed: true,
                limit,
                remaining: limit - currentCount - 1,
                reset: Math.ceil((now + (window * 1000)) / 1000)
            };

        } catch (error) {
            console.error('Rate limit check error:', error);
            // On error, allow the request but log it
            return {
                allowed: true,
                limit,
                remaining: limit - 1,
                reset: Math.ceil((now + (window * 1000)) / 1000),
                error: error.message
            };
        }
    }

    /**
     * Check daily limit for pay-per-use users
     */
    async checkDailyLimit(userId, dailyLimit = 10000) {
        const today = new Date().toISOString().split('T')[0];
        const key = `daily_limit:${userId}:${today}`;

        try {
            const current = await this.redis.get(key) || 0;

            if (parseInt(current) >= dailyLimit) {
                return {
                    allowed: false,
                    limit: dailyLimit,
                    used: parseInt(current),
                    remaining: 0
                };
            }

            // Increment counter
            await this.redis.incr(key);
            await this.redis.expire(key, 86400 + 3600); // 25 hours

            return {
                allowed: true,
                limit: dailyLimit,
                used: parseInt(current) + 1,
                remaining: dailyLimit - parseInt(current) - 1
            };

        } catch (error) {
            console.error('Daily limit check error:', error);
            return { allowed: true, limit: dailyLimit, used: 0, remaining: dailyLimit };
        }
    }
}

/**
 * Usage Tracker using Upstash Redis
 * Tracks API usage for billing
 */
class VerityUsageTracker {
    constructor(redis) {
        this.redis = redis;
    }

    /**
     * Track a verification request
     */
    async trackUsage(userId, verificationType = 'standard', costCents = 6) {
        const now = new Date();
        const monthKey = `usage:${userId}:${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        const dayKey = `usage:${userId}:${now.toISOString().split('T')[0]}`;

        try {
            // Increment monthly counters
            await this.redis.hincrby(monthKey, 'total_count', 1);
            await this.redis.hincrby(monthKey, `${verificationType}_count`, 1);
            await this.redis.hincrby(monthKey, 'total_cost_cents', costCents);
            await this.redis.expire(monthKey, 86400 * 35); // 35 days

            // Increment daily counter
            await this.redis.incr(dayKey);
            await this.redis.expire(dayKey, 86400 * 2); // 2 days

            return { success: true };
        } catch (error) {
            console.error('Usage tracking error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get usage for current month
     */
    async getMonthlyUsage(userId) {
        const now = new Date();
        const monthKey = `usage:${userId}:${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

        try {
            const data = await this.redis.hgetall(monthKey);
            if (!data) {
                return {
                    total_count: 0,
                    standard_count: 0,
                    premium_count: 0,
                    bulk_count: 0,
                    total_cost_cents: 0
                };
            }

            // Parse the result (comes as alternating key/value array)
            const usage = {};
            for (let i = 0; i < data.length; i += 2) {
                usage[data[i]] = parseInt(data[i + 1]) || 0;
            }

            return {
                total_count: usage.total_count || 0,
                standard_count: usage.standard_count || 0,
                premium_count: usage.premium_count || 0,
                bulk_count: usage.bulk_count || 0,
                total_cost_cents: usage.total_cost_cents || 0,
                total_cost: (usage.total_cost_cents || 0) / 100
            };
        } catch (error) {
            console.error('Get usage error:', error);
            return { total_count: 0, total_cost: 0 };
        }
    }

    /**
     * Get daily usage for charts
     */
    async getDailyUsage(userId, days = 30) {
        const usage = [];
        const now = new Date();

        for (let i = 0; i < days; i++) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            const dayKey = `usage:${userId}:${date.toISOString().split('T')[0]}`;

            try {
                const count = await this.redis.get(dayKey) || 0;
                usage.push({
                    date: date.toISOString().split('T')[0],
                    count: parseInt(count)
                });
            } catch (error) {
                usage.push({ date: date.toISOString().split('T')[0], count: 0 });
            }
        }

        return usage.reverse();
    }
}

/**
 * Session Cache using Upstash Redis
 * Caches user sessions and API keys
 */
class VeritySessionCache {
    constructor(redis) {
        this.redis = redis;
    }

    /**
     * Cache API key validation result
     */
    async cacheApiKey(keyHash, userData, ttl = 300) {
        const key = `api_key:${keyHash}`;
        try {
            await this.redis.set(key, JSON.stringify(userData), { ex: ttl });
            return true;
        } catch (error) {
            console.error('Cache API key error:', error);
            return false;
        }
    }

    /**
     * Get cached API key data
     */
    async getCachedApiKey(keyHash) {
        const key = `api_key:${keyHash}`;
        try {
            const data = await this.redis.get(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Get cached API key error:', error);
            return null;
        }
    }

    /**
     * Invalidate API key cache
     */
    async invalidateApiKey(keyHash) {
        const key = `api_key:${keyHash}`;
        try {
            await this.redis.del(key);
            return true;
        } catch (error) {
            console.error('Invalidate API key error:', error);
            return false;
        }
    }

    /**
     * Cache verification result
     */
    async cacheVerification(claimHash, result, ttl = 3600) {
        const key = `verification:${claimHash}`;
        try {
            await this.redis.set(key, JSON.stringify(result), { ex: ttl });
            return true;
        } catch (error) {
            console.error('Cache verification error:', error);
            return false;
        }
    }

    /**
     * Get cached verification
     */
    async getCachedVerification(claimHash) {
        const key = `verification:${claimHash}`;
        try {
            const data = await this.redis.get(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Get cached verification error:', error);
            return null;
        }
    }
}

// Initialize and export
const redis = new UpstashRedis();
const rateLimiter = new VerityRateLimiter(redis);
const usageTracker = new VerityUsageTracker(redis);
const sessionCache = new VeritySessionCache(redis);

// Export for Python backend (via environment or config)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        UpstashRedis,
        VerityRateLimiter,
        VerityUsageTracker,
        VeritySessionCache,
        redis,
        rateLimiter,
        usageTracker,
        sessionCache
    };
}

// Export for browser/frontend
if (typeof window !== 'undefined') {
    window.VerityRedis = {
        redis,
        rateLimiter,
        usageTracker,
        sessionCache
    };
}

console.log('✅ Upstash Redis client initialized');
