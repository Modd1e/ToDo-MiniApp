from fastapi import APIRouter

from .root import router as root_router
from .webhook import router as webhook_router
from .user import router as user_router

api_routers = APIRouter()

api_routers.include_router(root_router)
api_routers.include_router(webhook_router)
api_routers.include_router(user_router)
