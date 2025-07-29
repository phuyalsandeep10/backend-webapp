import requests


def get_login_token():
    try:
        res = requests.post(
            "http://localhost:8000/auth/login",
            json={"email": "test@gmail.com", "password": "test12345"},
        )
        data = res.json()
        return data["data"]["access_token"]
    except Exception as e:
        print(e)
