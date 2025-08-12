import os

import httpx

from src.config.settings import settings


def is_production_env():
    return settings.ENV == "production"


async def get_location(ip: str):
    """retrieve location data from ip-api.com"""
    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()
        if data.get("status") != "success":
            return {
                "ip": ip,
                "latitude": "",
                "longitude": "",
                "city": "",
                "country": "",
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


def extract_subset_from_dict(superset: dict, subset: dict) -> dict:
    extracted_value = {k: superset[k] for k in subset.keys() if k in superset}
    return extracted_value
