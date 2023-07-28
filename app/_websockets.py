import json

from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.params import Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session

from aio_pika import connect, Message as pikaMessage, IncomingMessage

from helpers import generate_links, generate_link
from repository import MessageRepository

import asyncio

import auth


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def setup(self, queue_name: str):
        self.rmq_conn = await connect(
            host='127.0.0.1', port=5672,
            login='superadmin',
            password='superadmin',
            loop=asyncio.get_running_loop()
        )
        self.channel = await self.rmq_conn.channel()
        self.queue_name = queue_name
        queue = await self.channel.declare_queue(self.queue_name)
        await queue.consume(self._notify, no_ack=True)
        # self.is_ready = True

    async def push(self, msg: str):
        await self.channel.default_exchange.publish(
            pikaMessage(msg.encode("ascii")),
            routing_key=self.queue_name,
        )

    async def _notify(self, message: IncomingMessage):
        for connection in self.active_connections:
            await connection.send_text(f"{json.loads(message.body)}")
        # living_connections = []
        # _websocket = self.active_connections
        # while len(_websocket) > 0:
        #     _websocket = _websocket.pop()
        #     await _websocket.send_text(f"{message.body}")
        #     living_connections.append(_websocket)
        # self.connections = living_connections

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# async def auth():
#
#     async with aiohttp.ClientSession() as session:
#
#         pokemon_url = 'http://10.0.54.6:8007/auth/signup'
#         async with session.post(pokemon_url) as resp:
#             pokemon = await resp.json()
#             print(pokemon)

def get_current_user():
    return []


# async def get_cookie_or_token(
#     websocket: WebSocket,
#     session: Annotated[str | None, Cookie()] = None,
#     token: Annotated[str | None, Query()] = None,
# ):
#     if session is None and token is None:
#         raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
#     return session or token

async def load(websocket: WebSocket, stmt_id: UUID,
               db: AsyncSession = Depends(get_session),
               access_token=Cookie(...)
               ):
    auth.get_current_user(access_token)

    await manager.connect(websocket)
    _db = MessageRepository(db)
    try:
        messages = await _db.find_messages_by_stmt(stmt_id)
        await manager.send_personal_message(f"{generate_links(stmt_id, messages, websocket.base_url.netloc)}",
                                            websocket)

        while True:
            await manager.setup("hello")
            data = await websocket.receive_json()
            print(data)
            await _db.add_one(data, stmt_id)

            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"{generate_link(stmt_id, data, websocket.base_url.netloc)}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{stmt_id} left the chat")
