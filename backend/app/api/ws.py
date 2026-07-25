from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):

    if not session_id.strip():
        await websocket.close(code=1008)
        return

    logger.info("=" * 60)
    logger.info(f"Incoming WebSocket Connection: {session_id}")
    logger.info("=" * 60)

    await manager.connect(
        session_id=session_id,
        websocket=websocket,
    )

    try:

        while True:

            message = await websocket.receive_text()

            if not message.strip():
                continue

            logger.info(
                f"[{session_id}] Received: {message}"
            )

            # Heartbeat support
            if message.lower() == "ping":

                await websocket.send_text("pong")

    except WebSocketDisconnect:

        logger.info(
            f"WebSocket disconnected: {session_id}"
        )

    except Exception:

        logger.exception(
            f"WebSocket error: {session_id}"
        )

    finally:

        manager.disconnect(session_id)

        logger.info(
            f"Connection closed: {session_id}"
        )