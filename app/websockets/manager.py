from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # Store active connections by board_id
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, board_id: str):
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
        self.active_connections[board_id].append(websocket)

    def disconnect(self, websocket: WebSocket, board_id: str):
        if board_id in self.active_connections:
            self.active_connections[board_id].remove(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]

    async def broadcast_to_board(self, board_id: str, message: dict):
        if board_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[board_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection, board_id)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()
