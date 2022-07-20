from typing import List

from starlette.websockets import WebSocket

from db import SessionLocal
from user import models
from user.jwt_handler import decode_jwt


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = {}
        self.db = SessionLocal()

    def is_current_user_access(self, chat_id: int, client_token: str):
        user = decode_jwt(client_token)
        return self.db.query(models.User).get(user["user_id"]) in self.db.query(models.ChatRoom).get(chat_id).users

    async def connect(self, websocket: WebSocket, chat_id: int, client_token: str):
        await websocket.accept()
        if self.is_current_user_access(chat_id, client_token):
            if chat_id not in self.active_connections.keys():
                self.active_connections[chat_id] = []
            self.active_connections[chat_id].append(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        self.active_connections[chat_id].remove(websocket)

    async def broadcast(self, message: str, chat_id: int, client_token: str, websocket: WebSocket):
        if self.is_current_user_access(chat_id, client_token):
            for connection in self.active_connections[chat_id]:
                if connection != websocket:
                    await connection.send_json(message)
