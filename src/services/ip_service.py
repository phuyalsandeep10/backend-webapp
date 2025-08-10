import httpx

class IPService:
    
    @staticmethod
    def get_ip_info(ip_address: str) -> dict:
        """Get geolocation and ISP info for IP address"""
        print("ip ", ip_address)
        # test_ip = '49.244.92.113'
        resp = httpx.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,message,lat,lon,city,country"
        )
        data = resp.json()

        if data.get("status") != "success":
            return {
                "ip": ip_address,
                "latitude": "",
                "longitude": "",
                "city": "",
                "country": "",
            }

        return {
            "ip": ip_address,
            "latitude": data["lat"],
            "longitude": data["lon"],
            "city": data["city"],
            "country": data["country"],
        }
