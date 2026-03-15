from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from core.connection_manager import manager
from services.openai_service import OpenAIService
from services.sentence_splitter import SentenceSplitter
from core.config import get_settings
import logging
import traceback

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Khởi tạo OpenAI Service với model từ cấu hình
openai_service = OpenAIService(
    api_key=settings.openai_api_key,
    llm_model=settings.openai_llm_model,
    tts_model=settings.openai_tts_model
)

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    splitter = SentenceSplitter()
    
    logger.info(f"Client {client_id} đã kết nối. Sử dụng model: {settings.openai_llm_model}")
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_data = message["bytes"]
                try:
                    logger.info(f"Đang xử lý {len(audio_data)} bytes âm thanh từ {client_id}...")
                    
                    text = await openai_service.stt(audio_data)
                    
                    if not text or len(text.strip()) <= 1:
                        logger.info("Không nhận dạng được lời nói.")
                        continue

                    logger.info(f"User ({client_id}): {text}")
                    
                    async for token in openai_service.llm_stream(text):
                        sentence = splitter.append_token(token)
                        if sentence:
                            logger.info(f"Sophia: {sentence}")
                            audio_response = await openai_service.tts(sentence)
                            await manager.send_personal_bytes(audio_response, client_id)
                    
                    last_sentence = splitter.get_remaining()
                    if last_sentence:
                        logger.info(f"Sophia: {last_sentence}")
                        audio_response = await openai_service.tts(last_sentence)
                        await manager.send_personal_bytes(audio_response, client_id)

                except Exception as e:
                    error_msg = f"Lỗi xử lý AI Pipeline: {str(e)}"
                    logger.error(error_msg)
                    await manager.send_personal_message({"type": "error", "message": error_msg}, client_id)
                    
            elif "text" in message:
                logger.info(f"Tín hiệu điều khiển: {message['text']}")
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} đã thoát.")
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Lỗi hệ thống WebSocket: {str(e)}")
        manager.disconnect(client_id)
