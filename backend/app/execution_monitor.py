import asyncio
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket


class ExecutionMonitorManager:
    """Manage WebSocket connections for execution monitoring."""

    def __init__(self) -> None:
        self.connections: Dict[int, List[WebSocket]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def connect(self, execution_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self.lock:
            self.connections[execution_id].append(websocket)

    async def disconnect(self, execution_id: int, websocket: WebSocket) -> None:
        async with self.lock:
            if websocket in self.connections.get(execution_id, []):
                self.connections[execution_id].remove(websocket)

    async def broadcast(self, execution_id: int, message: dict) -> None:
        async with self.lock:
            clients = list(self.connections.get(execution_id, []))
        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(execution_id, ws)

    def broadcast_sync(self, execution_id: int, message: dict) -> None:
        asyncio.create_task(self.broadcast(execution_id, message))


monitor_manager = ExecutionMonitorManager()
