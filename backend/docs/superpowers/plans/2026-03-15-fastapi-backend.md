# FastAPI AI Backend Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng một AI Backend Server bằng FastAPI kết nối với ESP32 qua WebSocket, cung cấp luồng xử lý Audio (STT, TTS), LLM, và MCP (điều khiển thiết bị).

**Architecture:** Sử dụng FastAPI làm entry point với Uvicorn cho WebSockets. Hệ thống được chia thành `core` (Cấu hình và Quản lý kết nối), `api` (WebSocket Router), và `services` (Xử lý âm thanh, OpenAI STT/TTS/LLM, MCP Controller). Đầu vào âm thanh dạng Opus sẽ được giải mã thành PCM rồi gửi đến các dịch vụ đám mây.

**Tech Stack:** FastAPI, Uvicorn, OpenAI Python SDK, Opuslib (cho decode/encode), Pytest, WebSockets.

---

## Chunk 1: Setup, Config, and Connection Manager

### Task 1: Project Setup and Configuration

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/core/config.py`
- Create: `backend/tests/core/test_config.py`

- [ ] **Step 1: Write requirements.txt**
```text
fastapi==0.110.0
uvicorn[standard]==0.27.1
websockets==12.0
openai==1.13.3
opuslib==3.0.1
pytest==8.0.2
pytest-asyncio==0.23.5
python-dotenv==1.0.1
```

- [ ] **Step 2: Write failing test for config**
```python
# backend/tests/core/test_config.py
import os
from core.config import get_settings

def test_config_loads_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    settings = get_settings()
    assert settings.openai_api_key == "test-key-123"
    assert settings.ws_host == "0.0.0.0"
    assert settings.ws_port == 8000
```

- [ ] **Step 3: Run test to verify it fails**
Run: `cd backend && pytest tests/core/test_config.py -v`
Expected: FAIL with ModuleNotFoundError for core.config

- [ ] **Step 4: Write minimal implementation for config**
```python
# backend/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str = ""
    ws_host: str = "0.0.0.0"
    ws_port: int = 8000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

- [ ] **Step 5: Run test to verify it passes**
Run: `cd backend && pytest tests/core/test_config.py -v`
Expected: PASS

- [ ] **Step 6: Commit**
```bash
git add backend/requirements.txt backend/core/config.py backend/tests/core/test_config.py
git commit -m "feat(backend): init requirements and config module"
```

### Task 2: WebSocket Connection Manager

**Files:**
- Create: `backend/core/connection_manager.py`
- Create: `backend/tests/core/test_connection_manager.py`

- [ ] **Step 1: Write failing test for Connection Manager**
```python
# backend/tests/core/test_connection_manager.py
import pytest
from core.connection_manager import ConnectionManager

class MockWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent_data = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent_data.append(data)

@pytest.mark.asyncio
async def test_connection_manager():
    manager = ConnectionManager()
    ws = MockWebSocket()
    
    await manager.connect(ws, "client-1")
    assert ws.accepted == True
    assert "client-1" in manager.active_connections
    
    await manager.send_personal_message({"action": "test"}, "client-1")
    assert len(ws.sent_data) == 1
    
    manager.disconnect("client-1")
    assert "client-1" not in manager.active_connections
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/core/test_connection_manager.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**
```python
# backend/core/connection_manager.py
from fastapi import WebSocket
from typing import Dict, Any

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: Any, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def send_personal_bytes(self, data: bytes, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_bytes(data)

manager = ConnectionManager()
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/core/test_connection_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/core/connection_manager.py backend/tests/core/test_connection_manager.py
git commit -m "feat(backend): add websocket connection manager"
```

---

## Chunk 2: Audio Processor & MCP Controller

### Task 3: Audio Processor Placeholder

**Files:**
- Create: `backend/services/audio_processor.py`
- Create: `backend/tests/services/test_audio_processor.py`

- [ ] **Step 1: Write test for audio processor decoder**
```python
# backend/tests/services/test_audio_processor.py
import pytest
from services.audio_processor import OpusDecoder

def test_opus_decoder_init():
    # Placeholder test since opuslib requires binary dependencies (libopus)
    decoder = OpusDecoder(sample_rate=16000, channels=1)
    assert decoder.sample_rate == 16000
    
def test_opus_decode_placeholder():
    decoder = OpusDecoder()
    pcm = decoder.decode(b'fake_opus_data')
    assert pcm == b'' # Placeholder behavior until real stream
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/services/test_audio_processor.py -v`
Expected: FAIL ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**
```python
# backend/services/audio_processor.py
class OpusDecoder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        # Note: True opuslib implementation will go here later
        
    def decode(self, opus_data: bytes) -> bytes:
        # Placeholder for decode logic
        # return opuslib.Decoder(self.sample_rate, self.channels).decode(opus_data, 960)
        return b''
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/services/test_audio_processor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/services/audio_processor.py backend/tests/services/test_audio_processor.py
git commit -m "feat(backend): add audio processor placeholder for opus decoding"
```

### Task 4: MCP Controller

**Files:**
- Create: `backend/services/mcp_controller.py`
- Create: `backend/tests/services/test_mcp_controller.py`

- [ ] **Step 1: Write test for MCP Controller**
```python
# backend/tests/services/test_mcp_controller.py
from services.mcp_controller import process_function_call

def test_process_function_call_led():
    call_data = {"name": "turn_on_led", "arguments": '{"color": "red"}'}
    result = process_function_call(call_data)
    assert result == {"action": "turn_on_led", "color": "red"}

def test_process_function_call_unknown():
    call_data = {"name": "unknown", "arguments": '{}'}
    result = process_function_call(call_data)
    assert result == {"error": "Unknown function"}
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/services/test_mcp_controller.py -v`
Expected: FAIL ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**
```python
# backend/services/mcp_controller.py
import json

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "turn_on_led",
            "description": "Bật đèn LED trên thiết bị",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {"type": "string", "description": "Màu của đèn LED (ví dụ: red, blue)"}
                },
                "required": ["color"]
            }
        }
    }
]

def process_function_call(call_data: dict) -> dict:
    name = call_data.get("name")
    args_str = call_data.get("arguments", "{}")
    
    try:
        args = json.loads(args_str)
    except:
        args = {}
        
    if name == "turn_on_led":
        return {"action": "turn_on_led", **args}
        
    return {"error": "Unknown function"}
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/services/test_mcp_controller.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/services/mcp_controller.py backend/tests/services/test_mcp_controller.py
git commit -m "feat(backend): add MCP Controller for function calling"
```

---

## Chunk 3: API & Application Integration

### Task 5: WebSocket Router

**Files:**
- Create: `backend/api/websocket.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write WebSocket endpoint logic**
```python
# backend/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

- [ ] **Step 2: Setup Main FastAPI App**
```python
# backend/main.py
from fastapi import FastAPI
from api.websocket import router as websocket_router

app = FastAPI(title="Sophia AI Backend")

app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Sophia Backend Running"}
```

- [ ] **Step 3: Create App Test**
Create `backend/tests/test_main.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Sophia Backend Running"}

def test_websocket_connect():
    with client.websocket_connect("/ws/audio/test-client") as websocket:
        websocket.send_text("Hello")
        # Just ensure it connects without dropping immediately
        pass
```

- [ ] **Step 4: Run tests**
Run: `cd backend && pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/api/websocket.py backend/main.py backend/tests/test_main.py
git commit -m "feat(backend): add websocket endpoint and main app setup"
```
