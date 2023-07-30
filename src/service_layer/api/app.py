"""Main FastAPI src instance declaration."""
from _websockets import websocket_endpoint, load
from fastapi import FastAPI
from api import api_router
import sys

sys.path.append("//api/routers")

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/",
)
app.include_router(api_router)

app.add_api_websocket_route('/ws', websocket_endpoint)
app.add_api_websocket_route('/ws/{stmt_id}', load)
