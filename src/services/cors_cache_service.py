from .redis_service import RedisService
from src.models import Organization


import json

CACHE_TTL = 600  # 10 minutes


class CORSCacheService:

    @staticmethod
    async def get_org(org_id: str):
        redis = await RedisService.get_redis()
        if not org_id:
            return None

        cache_key = f"org:{org_id}"
        
        # Try to get from Redis
        org = (await redis.get(cache_key)).decode('utf-8') if await redis.get(cache_key) else None

        if org:
            return json.loads(org)

        # Fetch from DB if not in cache
        org = await Organization.find_one({"identifier": org_id})

        if org:
            # Store in Redis with TTL
            await redis.set(cache_key, json.dumps(org.to_json()), ex=CACHE_TTL)
            return org.to_json()

        return None
    
    @staticmethod
    async def update_org_domain(org_id:str,org:dict):

        redis = await RedisService.get_redis()
        await redis.set(f"org:{org_id}", json.dumps(org), ex=CACHE_TTL)
