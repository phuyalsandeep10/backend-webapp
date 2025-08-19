from fastapi import FastAPI

from src.modules.admin.router import router as admin_router
from src.modules.auth.router import router as auth_router
from src.modules.chat.routers.conversation import router as conversation_router
from src.modules.chat.routers.customer import router as customer_router
from src.modules.organizations.router import router as organization_router
from src.modules.team.router import router as team_router
from src.modules.ticket.routers import router as ticket_router
from src.modules.upload.router import router as upload_router
from src.modules.chat.routers.agent import router as agent_chat_router


def add_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(
        organization_router, prefix="/organizations", tags=["organizations"]
    )
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(team_router, prefix="/teams", tags=["teams"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])
    app.include_router(customer_router, prefix="/p/customers", tags=["customers"])
    app.include_router(
        conversation_router, prefix="/conversations", tags=["conversations"]
    )
    app.include_router(agent_chat_router, prefix="/agent-chat", tags=["agents"])
    app.include_router(ticket_router, tags=["ticket"])
