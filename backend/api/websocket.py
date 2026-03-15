from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from core.connection_manager import manager

router = APIRouter()

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # We handle binary and text differently
            message = await websocket.receive()
            if "bytes" in message:
                data = message["bytes"]
                # TODO: Pass to Audio Processor -> STT -> LLM
                pass
            elif "text" in message:
                text_data = message["text"]
                # TODO: Handle control signals
                pass
    except (WebSocketDisconnect, RuntimeError):
        # RuntimeError: Cannot call "receive" once a disconnect message has been received
        manager.disconnect(client_id)
