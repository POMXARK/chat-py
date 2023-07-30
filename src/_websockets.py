import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.params import Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from dal.postgres.db import get_session
from aio_pika import connect, Message as pikaMessage, IncomingMessage
from helpers import generate_links, generate_link
from dal.postgres.repositories.repository import MessageRepository
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

    async def push(self, msg: str):
        await self.channel.default_exchange.publish(
            pikaMessage(msg.encode("ascii")),
            routing_key=self.queue_name,
        )

    async def _notify(self, message: IncomingMessage):
        for connection in self.active_connections:
            await connection.send_text(f"{json.loads(message.body)}")

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


def get_current_user():
    return []


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

            await manager.broadcast(f"{generate_link(stmt_id, data, websocket.base_url.netloc)}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{stmt_id} left the chat")
