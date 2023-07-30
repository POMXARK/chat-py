from fastapi import APIRouter
from routers.message import message

api_router = APIRouter()
api_router.include_router(message.router, prefix="/chat", tags=["chat"])
