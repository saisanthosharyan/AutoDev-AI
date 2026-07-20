from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    await manager.connect(
        session_id=session_id,
        websocket=websocket,
    )

    try:
        while True:
            # Keep the connection alive.
            # The frontend can optionally send ping messages.
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(session_id)

    except Exception:
        manager.disconnect(session_id)