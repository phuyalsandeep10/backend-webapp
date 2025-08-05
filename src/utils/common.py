import os
import httpx
def is_production_env():
    return os.getenv("ENV", "development") == "production"

async def get_location(ip: str):
    """retrieve location data from ip-api.com"""
    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()
        if data.get("status") != "success":
            return {
                "ip": ip,
                "latitude": None,
                "longitude": None,
                "city": None,
                "country": None,
            }
        return {
            "ip": ip,
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "city": data.get("city"),
            "country": data.get("country"),
            "regionName": data.get("regionName"),
            "zip": data.get("zip"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "as": data.get("as"),
            "query": data.get("query"),
        }
  