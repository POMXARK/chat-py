"""Main FastAPI src instance declaration."""
from _websockets import websocket_endpoint, load

import sys

print(sys.path)

sys.path.append("//api/endpoints")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.api import api_router
from src.core import config

app = FastAPI(
    #title=config.settings.PROJECT_NAME,
    #version=config.settings.VERSION,
    #description=config.settings.DESCRIPTION,
    openapi_url="/openapi.json",
    docs_url="/",
)
app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in config.settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guards against HTTP Host Header attacks
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.settings.ALLOWED_HOSTS)


app.add_api_websocket_route('/ws', websocket_endpoint)
app.add_api_websocket_route('/ws/{stmt_id}', load)
