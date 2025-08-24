from starlette.middleware.base import BaseHTTPMiddleware
from src.config.settings import settings
from src.models import Organization
from fastapi import Request, Response
from src.services.cors_cache_service import CORSCacheService


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
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        print(f"Request from origin: {origin}")
        
        path = request.url.path

                # Handle OPTIONS preflight requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        if origin and origin in ALLOWED_ORIGINS:
            self.setHeaders(response, origin)
            return response

        if not origin:
            # Don't set headers if origin is None
            return response

        if path.startswith("/customer"):
            org_id = request.headers.get("X-Org-ID")

            org = await CORSCacheService.get_org_domain(org_id)
            if org and origin == org.domain:
                self.setHeaders(response, origin)
                TenantContext.set(org.id)
                return response
                
        return Response("Forbidden", status_code=403)
    
