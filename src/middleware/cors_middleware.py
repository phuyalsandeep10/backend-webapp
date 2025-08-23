from starlette.middleware.base import BaseHTTPMiddleware
from src.config.settings import settings
from src.models import Organization
from fastapi import Request, Response
from src.services.cors_cache_service import CORSCacheService
from src.common.context import TenantContext

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.chatboq.com",
]



class CORSMiddleware(BaseHTTPMiddleware):
    def setHeaders(self, response, origin: str):
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type,X-Org-Id"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        path = request.url.path
        print(f"Request from origin: {origin}, path: {path}")

        # Handle OPTIONS preflight requests
        if request.method == "OPTIONS":
            response = Response()
            # Always set CORS headers for OPTIONS
            if origin in ALLOWED_ORIGINS:
                self.setHeaders(response, origin)
            else:
                # For OPTIONS, allow all origins but don't set Access-Control-Allow-Origin
                response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type,X-Org-Id"
                response.headers["Access-Control-Allow-Credentials"] = "true"
            response.status_code = 200
            return response

        # For actual requests, check origin first
        if not origin:
            return Response("Forbidden: No origin header", status_code=403)

        # Handle /customers path with organization check
        if path.startswith("/customers"):
            org_id = request.headers.get('x-org-id')
            if org_id:
                org = await CORSCacheService.get_org(org_id)
                if org and (origin in ALLOWED_ORIGINS or org.get('domain') == origin):
                    print(f"Setting organization id {org.get('id')}")
                    TenantContext.set(org.get('id'))
                    response = await call_next(request)
                    self.setHeaders(response, origin)
                    return response
                return Response("Forbidden: Organization not found or origin not allowed", status_code=403)

        # For all other paths, check against allowed origins
        if origin in ALLOWED_ORIGINS:
            response = await call_next(request)
            self.setHeaders(response, origin)
            return response
        
        return Response("Forbidden: Origin not allowed", status_code=403)
    
