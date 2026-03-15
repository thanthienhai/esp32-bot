from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from core.connection_manager import manager
from services.openai_service import OpenAIService
from services.sentence_splitter import SentenceSplitter
from core.config import get_settings
import logging

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Khởi tạo OpenAI Service (Yêu cầu OPENAI_API_KEY trong môi trường)
openai_service = OpenAIService(api_key=settings.openai_api_key)

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    splitter = SentenceSplitter()
    
    # Buffer tạm thời để chứa dữ liệu âm thanh PCM (16kHz, 16-bit Mono)
    # Lưu ý: Trong thực tế ESP32 có thể gửi Opus, cần thêm bước decode
    pcm_buffer = bytearray()
    
    # Ngưỡng kích hoạt STT tạm thời (ví dụ: sau khi nhận được 3 giây âm thanh)
    # 16000 samples/sec * 2 bytes/sample * 3 seconds = 96000 bytes
    STT_THRESHOLD = 96000 
    
    logger.info(f"Client {client_id} connected to Sophia AI Backend")
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_data = message["bytes"]
                pcm_buffer.extend(audio_data)
                
                # Prototype logic: Nếu nhận đủ 1 khối âm thanh hoặc có tín hiệu ngắt (VAD)
                # Ở đây chúng ta tạm thời dùng ngưỡng kích thước để demo thông luồng
                if len(pcm_buffer) >= STT_THRESHOLD:
                    logger.info(f"Processing audio chunk for {client_id}...")
                    
                    # 1. Chuyển đổi Giọng nói thành Văn bản (STT)
                    text = await openai_service.stt(bytes(pcm_buffer))
                    pcm_buffer.clear() # Xóa buffer sau khi xử lý
                    
                    if text and len(text.strip()) > 1:
                        logger.info(f"User ({client_id}): {text}")
                        
                        # 2. Gửi văn bản tới LLM (Streaming) và xử lý phản hồi
                        async for token in openai_service.llm_stream(text):
                            # Tách câu để gọi TTS sớm
                            sentence = splitter.append_token(token)
                            if sentence:
                                logger.info(f"Sophia ({client_id}) sentence: {sentence}")
                                # 3. Tổng hợp Giọng nói (TTS) cho từng câu
                                audio_response = await openai_service.tts(sentence)
                                # 4. Gửi âm thanh phản hồi xuống Robot (Binary)
                                await manager.send_personal_bytes(audio_response, client_id)
                        
                        # Xử lý phần văn bản còn lại cuối cùng
                        last_sentence = splitter.get_remaining()
                        if last_sentence:
                            logger.info(f"Sophia ({client_id}) last sentence: {last_sentence}")
                            audio_response = await openai_service.tts(last_sentence)
                            await manager.send_personal_bytes(audio_response, client_id)
                            
            elif "text" in message:
                # Xử lý các lệnh điều khiển dạng JSON (nếu có)
                text_msg = message["text"]
                logger.info(f"Received control signal from {client_id}: {text_msg}")
                # Ví dụ: {"type": "stop_audio"} để ngắt ngang lời robot
                pass
                
    except (WebSocketDisconnect, RuntimeError):
        logger.info(f"Client {client_id} disconnected")
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Error in websocket loop for {client_id}: {str(e)}")
        manager.disconnect(client_id)
