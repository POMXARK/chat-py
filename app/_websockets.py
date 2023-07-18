import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.api.deps import get_session
from app.models import Message

from aio_pika import connect, Message as pikaMessage, IncomingMessage
import asyncio


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


def generate_links(stmt_id, messages, websocket):
    _list = []
    for message in messages:
        _message = jsonable_encoder(message)

        _files = []
        if isinstance(_message['file_path'], list):
            for _file in _message['file_path']:
                _files.append(
                    f"{websocket.base_url.netloc}/chat/download?stmt_id={stmt_id}&user_id={_message['user_id']}&file_id={_file['file_id']}&name={_file['name']}")

        _message['file_path'] = _files
        _list.append(_message)

    return json.dumps(_list)


def generate_link(stmt_id, message, websocket):
    _message = jsonable_encoder(message)

    _files = []
    if isinstance(_message['file_path'], list):
        for _file in _message['file_path']:
            _files.append(
                f"{websocket.base_url.netloc}/chat/download?stmt_id={stmt_id}&user_id={_message['user_id']}&file_id={_file['file_id']}&name={_file['name']}")

    _message['file_path'] = _files
    _list = []
    _list.append(_message)

    return json.dumps(_list)


async def load(websocket: WebSocket, stmt_id: UUID, db: AsyncSession = Depends(get_session)):
    await manager.connect(websocket)

    try:
        query = select(Message).where(Message.stmt_id == stmt_id)
        messages = (await db.scalars(query)).all()

        await manager.send_personal_message(f"{generate_links(stmt_id, messages, websocket)}", websocket)

        while True:
            await manager.setup("hello")
            data = await websocket.receive_json()

            _message = Message(
                text=data['text'],
                stmt_id=stmt_id,
                user_id=data['user_id'],
                file_path=data['file_path']
            )
            db.add(_message)
            try:
                await db.commit()
            except Exception as e:
                                                                                                                                                                                                                                                                                                                return e

                                                                                                                                                                                                                                                                                                            # await manager.send_personal_message(f"You wrote: {data}", websocket)
                                                                                                                                                                                                                                                                                                            await manager.broadcast(f"{generate_link(stmt_id, data, websocket)}")
                                                                                                                                                                                                                                                                                                    except WebSocketDisconnect:
                                                                                                                                                                                                                                                                                                        manager.disconnect(websocket)
                                                                                                                                                                                                                                                                                                        await manager.broadcast(f"Client #{stmt_id} left the chat")
