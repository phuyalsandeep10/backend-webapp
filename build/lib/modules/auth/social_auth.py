from authlib.integrations.starlette_client import OAuth

from src.config.settings import settings


oauth = OAuth()

# Register the Google OAuth provider
# Register Google OAuth provider
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# Register Apple OAuth provider
oauth.register(
    name="apple",
    client_id=settings.APPLE_CLIENT_ID,
    client_secret=settings.APPLE_CLIENT_SECRET,
    server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email name"},
)
