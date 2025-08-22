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
        print(f"Request from origin: {origin}")
        
        path = request.url.path

                # Handle OPTIONS preflight requests
                
        if request.method == "OPTIONS":
            response = Response()
            # Always set CORS headers for OPTIONS
            if origin and origin in ALLOWED_ORIGINS:
                self.setHeaders(response, origin)
            else:
                # Allow OPTIONS for unknown origins, but do not set Allow-Origin
                response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type,X-Org-Id"
                response.headers["Access-Control-Allow-Credentials"] = "true"
            response.status_code = 200
            return response
        else:
            if not origin:
                # Don't set headers if origin is None
                return Response("Forbidden", status_code=403)
            response = await call_next(request)
            print(f"path {path}")
            if path.startswith("/customer"):
                org_id = request.headers.get('x-org-id')
                if org_id:
                    org = await CORSCacheService.get_org(org_id)
                    print(f"origin {origin}")
                    print(f"org domain {org.get('domain')} for org_id {org_id}")
                    if org :
                        print("organization id",org.get('id'))
                        self.setHeaders(response, origin)
                        TenantContext.set(org.get('id'))
                        return response
            elif origin in ALLOWED_ORIGINS:
                self.setHeaders(response, origin)
                return response
            return Response("Forbidden", status_code=403)
    
