"""WebSocket Alert Manager — Broadcast real-time alerts đến connected clients."""

import asyncio
import json
import logging
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class AlertManager:
    """Quản lý WebSocket connections và broadcast alert real-time."""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._connections.append(ws)
        logger.info(f"WebSocket connected. Total: {len(self._connections)}")

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            if ws in self._connections:
                self._connections.remove(ws)
        logger.info(f"WebSocket disconnected. Total: {len(self._connections)}")

    async def broadcast(self, message: dict):
        """Gửi message đến tất cả connected clients."""
        if not self._connections:
            return

        payload = json.dumps(message, default=str)
        dead: list[WebSocket] = []

        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        # Dọn connections chết
        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self._connections:
                        self._connections.remove(ws)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


# Singleton
alert_manager = AlertManager()
