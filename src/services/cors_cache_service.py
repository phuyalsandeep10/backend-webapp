from .redis_service import RedisService
CACHE_TTL = 600  # 10 minutes


class CORSCacheService:

    @staticmethod
    async def get_org_domain(org_id: str):
        redis = await RedisService.get_redis()
        if not org_id:
            return None

        cache_key = f"org_domain:{org_id}"
        
        # Try to get from Redis
        domain = await redis.get(cache_key)
        if domain:
            return domain

        # Fetch from DB if not in cache
        org = await Organization.find_one({"id": org_id})
        if org:
            domain = org.domain
            # Store in Redis with TTL
            await redis.set(cache_key, domain, ex=CACHE_TTL)
            return domain

        return None
    
    @staticmethod
    async def update_org_domain(org_id:str,domain:str):

        redis = await RedisService.get_redis()
        await redis.set(f"org_domain:{org_id}", domain, ex=CACHE_TTL)
    