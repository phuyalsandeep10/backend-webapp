import random
from passlib.context import CryptContext
import httpx


def generate_numeric_token(length: int = 6) -> str:
    if length < 4:
        raise ValueError("Token length must be at least 1")
    min_value = 10 ** (length - 1)
    max_value = (10**length) - 1
    return str(random.randint(min_value, max_value))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def compare_password(hashed_password: str, password: str) -> bool:
    """
    Compare two passwords to check if they are the same.
    """
    return pwd_context.verify(password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)


def generate_refresh_token(length: int = 32) -> dict:
    """
    Generate a random refresh token of specified length.
    The default length is set to 32 characters.
    """

    if length < 32:
        raise ValueError("Token length must be at least 3")
    return "".join(
        random.choices(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=length
        )
    )


def lookup_geo(ip: str) -> dict:
    print("ip ", ip)
    # test_ip = '49.244.92.113'
    resp = httpx.get(
        f"http://ip-api.com/json/{ip}?fields=status,message,lat,lon,city,country"
    )
    data = resp.json()

    if data.get("status") != "success":
        raise ValueError(data.get("message", "Failed lookup"))

    return {
        "ip": ip,
        "latitude": data["lat"],
        "longitude": data["lon"],
        "city": data["city"],
        "country": data["country"],
    }
    return data
