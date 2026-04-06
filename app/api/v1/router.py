from fastapi import APIRouter
from app.api.v1.endpoints import auth, ideas, messages

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(ideas.router)
api_router.include_router(messages.router)
