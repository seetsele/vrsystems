"""
Validate Upstash connectivity using `python-tools/upstash_redis.py`'s client.
Run: `python validate_upstash.py`
"""
import asyncio
import os

async def main():
    try:
        from upstash_redis import UpstashRedis
    except Exception as e:
        print('upstash_redis module not importable:', e)
        return

    url = os.getenv('UPSTASH_REDIS_REST_URL')
    token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    client = UpstashRedis(url, token)

    print('Testing SET/GET...')
    ok = await client.set('verity_test:ping', 'pong', ex=10)
    print('SET:', ok)
    val = await client.get('verity_test:ping')
    print('GET:', val)

if __name__ == '__main__':
    asyncio.run(main())
