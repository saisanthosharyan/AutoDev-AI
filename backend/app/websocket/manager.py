from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logger import logger


class ConnectionManager:
    """
    Manages active WebSocket connections.
    """

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    # --------------------------------------------------
    # Connect
    # --------------------------------------------------

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        # Replace old connection if one exists
        old = self.active_connections.get(session_id)

        if (
            old
            and old.client_state == WebSocketState.CONNECTED
        ):
            try:
                await old.close()
            except Exception:
                pass

        self.active_connections[session_id] = websocket

        logger.info(
            f"WebSocket connected: {session_id}"
        )

    # --------------------------------------------------
    # Disconnect
    # --------------------------------------------------

    def disconnect(
        self,
        session_id: str,
    ):

        if session_id in self.active_connections:

            self.active_connections.pop(session_id)

            logger.info(
                f"WebSocket disconnected: {session_id}"
            )

    # --------------------------------------------------
    # Send JSON
    # --------------------------------------------------

    async def send_json(
        self,
        session_id: str,
        data: dict,
    ):

        websocket = self.active_connections.get(
            session_id
        )

        if websocket is None:
            return

        if websocket.client_state != WebSocketState.CONNECTED:

            self.disconnect(session_id)
            return

        try:

            await websocket.send_json(data)

        except Exception:

            logger.exception(
                f"Failed sending WebSocket message: {session_id}"
            )

            self.disconnect(session_id)

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    async def send_progress(
        self,
        session_id: str,
        step: str,
        progress: int,
        message: str,
    ):

        await self.send_json(
            session_id,
            {
                "type": "progress",
                "step": step,
                "progress": progress,
                "message": message,
            },
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    async def send_status(
        self,
        session_id: str,
        message: str,
    ):

        await self.send_json(
            session_id,
            {
                "type": "status",
                "message": message,
            },
        )

    # --------------------------------------------------
    # Error
    # --------------------------------------------------

    async def send_error(
        self,
        session_id: str,
        message: str,
    ):

        await self.send_json(
            session_id,
            {
                "type": "error",
                "message": message,
            },
        )

    # --------------------------------------------------
    # Complete
    # --------------------------------------------------

    async def send_complete(
        self,
        session_id: str,
        result: dict,
    ):

        await self.send_json(
            session_id,
            {
                "type": "complete",
                "result": result,
            },
        )

    # --------------------------------------------------
    # Broadcast
    # --------------------------------------------------

    async def broadcast(
        self,
        data: dict,
    ):

        disconnected = []

        for session_id, websocket in self.active_connections.items():

            try:

                if websocket.client_state == WebSocketState.CONNECTED:

                    await websocket.send_json(data)

                else:

                    disconnected.append(session_id)

            except Exception:

                disconnected.append(session_id)

        for session_id in disconnected:
            self.disconnect(session_id)

    # --------------------------------------------------
    # Stats
    # --------------------------------------------------

    @property
    def connection_count(self) -> int:

        return len(self.active_connections)


manager = ConnectionManager()