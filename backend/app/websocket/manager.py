from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_json(
        self,
        session_id: str,
        data: dict,
    ):
        websocket = self.active_connections.get(session_id)

        if (
            websocket
            and websocket.client_state == WebSocketState.CONNECTED
        ):
            await websocket.send_json(data)

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


manager = ConnectionManager()