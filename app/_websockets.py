import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.api.deps import get_session
from app.models import Message


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

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


async def load(websocket: WebSocket, stmt_id: UUID, db: AsyncSession = Depends(get_session)):
    await manager.connect(websocket)
    try:
        query = select(Message).where(Message.stmt_id == stmt_id)
        messages = (await db.scalars(query)).all()
        await manager.send_personal_message(f"{json.dumps([jsonable_encoder(message) for message in messages])}", websocket)

        while True:
            data = await websocket.receive_json()

            _message = Message(
                text=data['text'],
                stmt_id=stmt_id,
                from_user_id=data['from_'],
                to_user_id=data['to']
            )
            db.add(_message)
            try:
                await db.commit()
            except Exception as e:
                return e

            #await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{stmt_id} left the chat")
