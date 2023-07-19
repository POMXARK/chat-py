from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session

from aio_pika import connect, Message as pikaMessage, IncomingMessage
import asyncio

from helpers import generate_links, generate_link
from repository import MessageRepository


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
            await connection.send_text(f"{message.body}")
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


async def load(websocket: WebSocket, stmt_id: UUID,
               db: AsyncSession = Depends(get_session)
               ):
    await manager.connect(websocket)
    _db = MessageRepository(db)
    try:
        messages = await _db.find_messages_by_stmt(stmt_id)
        await manager.send_personal_message(f"{generate_links(stmt_id, messages, websocket.base_url.netloc)}", websocket)

        while True:
            await manager.setup("hello")
            data = await websocket.receive_json()
            await _db.add_one(data, stmt_id)

            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"{generate_link(stmt_id, data, websocket.base_url.netloc)}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{stmt_id} left the chat")
