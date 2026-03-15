# OpenAI Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tích hợp OpenAI API cho STT, LLM, TTS và xây dựng pipeline xử lý âm thanh thời gian thực cho Robot Sophia.

**Architecture:** Xây dựng `OpenAIService` để giao tiếp với OpenAI. Sử dụng cơ chế ngắt câu (sentence-level splitting) cho LLM stream để gọi TTS sớm, giảm thiểu độ trễ. Dữ liệu âm thanh được encode sang Opus trước khi gửi xuống ESP32.

**Tech Stack:** OpenAI Python SDK, FastAPI, Opuslib, Pytest.

---

## Chunk 1: OpenAI Service Core

### Task 1: Initialize OpenAI Service and STT

**Files:**
- Create: `backend/services/openai_service.py`
- Create: `backend/tests/services/test_openai_service.py`

- [ ] **Step 1: Write test for STT (Mocked)**
```python
# backend/tests/services/test_openai_service.py
import pytest
from unittest.mock import AsyncMock, patch
from services.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_stt_success():
    service = OpenAIService(api_key="test-key")
    with patch("services.openai_service.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.audio.transcriptions.create = AsyncMock(return_value=AsyncMock(text="Xin chào Sophia"))
        
        result = await service.stt(b"fake_audio_data")
        assert result == "Xin chào Sophia"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/services/test_openai_service.py -v`
Expected: FAIL ModuleNotFoundError

- [ ] **Step 3: Write implementation for OpenAIService STT**
```python
# backend/services/openai_service.py
import io
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def stt(self, audio_bytes: bytes) -> str:
        # Chuyển đổi bytes thành file-like object để gửi lên OpenAI
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "audio.wav"
        
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language="vi"
        )
        return response.text
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/services/test_openai_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/services/openai_service.py backend/tests/services/test_openai_service.py
git commit -m "feat(backend): add OpenAI STT service"
```

### Task 2: LLM Streaming Service

**Files:**
- Modify: `backend/services/openai_service.py`
- Modify: `backend/tests/services/test_openai_service.py`

- [ ] **Step 1: Write test for LLM Stream**
```python
# backend/tests/services/test_openai_service.py (append)
@pytest.mark.asyncio
async def test_llm_stream():
    service = OpenAIService(api_key="test-key")
    with patch("services.openai_service.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        # Mock stream response
        async def mock_gen():
            yield AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="Chào"))])
            yield AsyncMock(choices=[AsyncMock(delta=AsyncMock(content=" bạn"))])
            
        mock_client.chat.completions.create = AsyncMock(return_value=mock_gen())
        
        tokens = []
        async for chunk in service.llm_stream("Chào"):
            tokens.append(chunk)
        
        assert "".join(tokens) == "Chào bạn"
```

- [ ] **Step 2: Implement llm_stream**
```python
# backend/services/openai_service.py (add method)
    async def llm_stream(self, text: str, history: list = None):
        if history is None:
            history = []
        
        messages = [
            {"role": "system", "content": "Bạn là Sophia, một robot trợ lý thông minh người Việt Nam. Hãy trả lời ngắn gọn, lễ phép, thân thiện và luôn dùng Tiếng Việt."},
            *history,
            {"role": "user", "content": text}
        ]
        
        stream = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

- [ ] **Step 3: Run test and commit**

---

## Chunk 2: Sentence Splitting & TTS Service

### Task 3: Sentence Splitting Logic

**Files:**
- Create: `backend/services/sentence_splitter.py`
- Create: `backend/tests/services/test_sentence_splitter.py`

- [ ] **Step 1: Write test for sentence splitter**
```python
# backend/tests/services/test_sentence_splitter.py
from services.sentence_splitter import SentenceSplitter

def test_sentence_splitter():
    splitter = SentenceSplitter()
    results = []
    
    # Simulate streaming tokens
    for token in ["Chào ", "bạn. ", "Hôm ", "nay ", "thế ", "nào?"]:
        sentence = splitter.append_token(token)
        if sentence:
            results.append(sentence)
    
    # Remaining
    last = splitter.get_remaining()
    if last:
        results.append(last)
        
    assert results == ["Chào bạn.", "Hôm nay thế nào?"]
```

- [ ] **Step 2: Implement SentenceSplitter**
```python
# backend/services/sentence_splitter.py
import re

class SentenceSplitter:
    def __init__(self):
        self.buffer = ""
        self.sentence_end_regex = re.compile(r'.*[.!?;](\s|$)')

    def append_token(self, token: str) -> str:
        self.buffer += token
        if self.sentence_end_regex.match(self.buffer):
            sentence = self.buffer.strip()
            self.buffer = ""
            return sentence
        return None

    def get_remaining(self) -> str:
        remaining = self.buffer.strip()
        self.buffer = ""
        return remaining if remaining else None
```

- [ ] **Step 3: Run test and commit**

### Task 4: TTS Service (MP3 to Opus conversion placeholder)

**Files:**
- Modify: `backend/services/openai_service.py`
- Modify: `backend/tests/services/test_openai_service.py`

- [ ] **Step 1: Implement TTS call**
```python
# backend/services/openai_service.py (add method)
    async def tts(self, text: str) -> bytes:
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            response_format="mp3" # Or opus if supported directly
        )
        return await response.read()
```

- [ ] **Step 2: Run tests and commit**

---

## Chunk 3: Full Pipeline Integration

### Task 5: Integration in WebSocket Endpoint

**Files:**
- Modify: `backend/api/websocket.py`

- [ ] **Step 1: Update WebSocket logic to handle STT -> LLM -> TTS**
```python
# backend/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.connection_manager import manager
from services.openai_service import OpenAIService
from services.sentence_splitter import SentenceSplitter
from core.config import get_settings

router = APIRouter()
settings = get_settings()
openai_service = OpenAIService(api_key=settings.openai_api_key)

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    splitter = SentenceSplitter()
    pcm_buffer = bytearray()
    
    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                # Giả định ESP32 gửi PCM hoặc Opus
                # Cho prototype, ta gom buffer PCM
                pcm_buffer.extend(message["bytes"])
                
                # Logic VAD tạm thời: Nếu buffer đủ lớn (> 5s) thì trigger
                if len(pcm_buffer) > 16000 * 2 * 5: 
                    text = await openai_service.stt(bytes(pcm_buffer))
                    pcm_buffer.clear()
                    
                    if text:
                        # LLM Stream -> Sentence -> TTS -> Send
                        async for token in openai_service.llm_stream(text):
                            sentence = splitter.append_token(token)
                            if sentence:
                                audio_bytes = await openai_service.tts(sentence)
                                await manager.send_personal_bytes(audio_bytes, client_id)
                        
                        # Last sentence
                        last = splitter.get_remaining()
                        if last:
                            audio_bytes = await openai_service.tts(last)
                            await manager.send_personal_bytes(audio_bytes, client_id)
                            
            elif "text" in message:
                # Handle signals like "start_listening", "stop_listening"
                pass
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

- [ ] **Step 2: Run full integration check (manual or automated)**
- [ ] **Step 3: Commit**
