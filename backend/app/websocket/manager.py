"""WebSocket Connection Manager for real-time alerts."""
import json
from datetime import datetime
from fastapi import WebSocket
import logging

logger = logging.getLogger("alias.websocket")


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts events."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Broadcast a message string to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_event(self, event_type: str, event_id: int | str, payload: dict):
        """Broadcast a structured alert event to all connected clients."""
        message = json.dumps({
            "type": event_type,
            "event_id": str(event_id),
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        })
        await self.broadcast(message)
        logger.debug(f"Broadcast {event_type} to {len(self.active_connections)} clients")
