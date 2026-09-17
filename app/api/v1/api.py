from fastapi import APIRouter
from app.api.v1 import health
from app.api.v1 import auth
from app.api.v1 import roles
from app.api.v1 import permissions
from app.api.v1 import cases
from app.api.v1 import webhooks
from app.api.v1 import agent_tasks

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(agent_tasks.router, prefix="/agent-tasks", tags=["agent-tasks"])

from app.api.v1 import websockets
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])

from app.api.v1 import admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Additional routers will be included here in later phases (auth, users, cases, etc.)
