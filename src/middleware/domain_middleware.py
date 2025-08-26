from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.cors_cache_service import CORSCacheService
from src.common.context import TenantContext

class DomainMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_domains=None):
        super().__init__(app)

        self.allowed_domains = allowed_domains or [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
            "https://api.chatboq.com",
            "https://portal.chatboq.com"
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip domain validation for OPTIONS requests (handled by CORS)
        if request.method == "OPTIONS":
            return await call_next(request)

        origin = request.headers.get("origin")
        path = request.url.path

        

        if not origin:
            return await call_next(request)

        print(f"Request origin: {origin}")

        # check if path is /customers then check if org_id is present in header
        if path.startswith('/customers'):
            org_id = request.headers.get("x-org-id")
            print(f"org_id {org_id}")
            if org_id:
                org = await CORSCacheService.get_org(org_id)
                if org:
                    if origin in self.allowed_domains:
                        TenantContext.set(org.get("id"))
                        return await call_next(request)
                    
                    if org and org.get("domain") == origin:
                        TenantContext.set(org.get("id"))
                        return await call_next(request)
            
            return Response("Forbidden: Domain not allowed", status_code=403)


    
        # Check if origin is in allowed domains
        if origin in self.allowed_domains:
            return await call_next(request)

        

        # If we get here, domain is not allowed
        return Response("Forbidden: Domain not allowed", status_code=403)
