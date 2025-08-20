from starlette.middleware.base import BaseHTTPMiddleware
from src.config.settings import settings
from src.models import Organization
from fastapi import FastAPI, Request


ALLOWED_ORIGINS = settings.CORS_ORIGINS

class CORSMiddleware(BaseHTTPMiddleware):

    def setHeaders(self,response,origin:str):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        path = request.url.path
        print(f"Request to: {method} {path}")  # <-- log or check endpoint
        response: Response = await call_next(request)
        
        if origin and origin in ALLOWED_ORIGINS:
            self.setHeaders(response, origin)
            return response
        
        if path.startswith("/customer"):
            org = await Organization.find_one({"id": request.headers.get("X-Org-ID")})
            if origin == org.domain:
                self.setHeaders(response, origin)
                TenantContext.set(org.id)
                return response
            

        return Response("Forbidden", status_code=403)