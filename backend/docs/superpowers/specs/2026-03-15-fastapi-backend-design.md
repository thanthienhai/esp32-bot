# FastAPI AI Backend cho ESP32 Robot (Sophia) - Design Spec

**Ngày:** 2026-03-15
**Dự án:** Xiaozhi ESP32 Vietnam (Sophia) - AI Backend

## 1. Mục tiêu hệ thống
Phát triển một AI Backend Server bằng Python để xử lý luồng dữ liệu thời gian thực (real-time stream) giao tiếp với các thiết bị vi điều khiển ESP32 qua WebSocket. Server sẽ làm cầu nối giữa phần cứng, giải mã âm thanh, và các mô hình AI đám mây (OpenAI) để mang lại khả năng tương tác bằng giọng nói tự nhiên, độ trễ thấp và điều khiển được thiết bị (thông qua MCP - Model Context Protocol).

## 2. Kiến trúc & Công nghệ (Tech Stack)
- **Framework:** FastAPI (Python 3.10+) - Hỗ trợ tốt WebSockets bất đồng bộ.
- **Web Server:** Uvicorn (cung cấp môi trường ASGI).
- **Giao thức Mạng:** WebSockets (Cho luồng âm thanh hai chiều và điều khiển thiết bị).
- **Giải mã Âm thanh (Audio Processing):** `pyogg` / `opuslib` để giải mã luồng Opus (Binary) do ESP32 gửi lên thành PCM (Pulse Code Modulation) để xử lý tiếp.
- **AI Integration (Cloud API):** 
  - **STT (Speech-to-Text):** OpenAI Whisper API.
  - **LLM (Logic & Điều khiển):** OpenAI GPT-4o-mini (hoặc các model tương đương hỗ trợ Function Calling/Tool Use).
  - **TTS (Text-to-Speech):** OpenAI TTS API.

## 3. Luồng dữ liệu (Data Flow)

Hệ thống sẽ duy trì 1 connection WebSocket cho mỗi thiết bị (Session).

### 3.1. Upstream (Thiết bị -> Backend)
1. ESP32 thu âm, sử dụng VAD/AEC và mã hóa Opus thành các frame.
2. ESP32 gửi các gói Opus Binary qua WebSocket.
3. Backend (FastAPI WebSocket Endpoint) nhận gói dữ liệu.
4. Dịch vụ Audio Decoder giải nén Opus -> PCM audio chunk.
5. Khi nhận đủ 1 chunk âm thanh (hoặc nhận được tín hiệu VAD Stop từ client), Backend đẩy buffer PCM tới OpenAI Whisper API để lấy văn bản.
6. STT Text được đẩy vào Context Manager.

### 3.2. Processing (Backend -> LLM)
1. Backend gọi OpenAI LLM, gửi đoạn text vừa nhận kèm theo lịch sử chat và danh sách các "Tools" (tượng trưng cho MCP: `turn_on_led()`, `move_motor()`).
2. Nếu LLM trả về Text, chuẩn bị cho khâu TTS.
3. Nếu LLM trả về Function Call (Tool Use), Backend sẽ đóng gói thành JSON Command (ví dụ: `{"action": "turn_on_led"}`).

### 3.3. Downstream (Backend -> Thiết bị)
- **Luồng Lệnh (Control):** Gửi JSON qua WebSocket xuống ESP32 để kích hoạt phần cứng.
- **Luồng Âm thanh (Audio):** 
  1. Nếu nhận được text từ LLM, Backend gửi text tới OpenAI TTS.
  2. OpenAI trả về Audio stream/file.
  3. (Tùy chọn) Encode lại Audio thành Opus (hoặc giữ nguyên định dạng thiết bị hỗ trợ) rồi stream dạng Binary xuống qua WebSocket.
  4. ESP32 nhận, decode và phát loa.

## 4. Cấu trúc Thư mục (Directory Structure)

```text
backend/
├── main.py                     # Entry point FastAPI & WebSocket router
├── requirements.txt            # Danh sách thư viện (fastapi, uvicorn, openai, opuslib...)
├── core/                       # Cấu hình lõi
│   ├── config.py               # Load biến môi trường (OPENAI_API_KEY)
│   └── connection_manager.py   # Quản lý Session WebSocket (Connect, Disconnect)
├── api/                        # Chứa các endpoint router (nếu cần REST API)
│   └── websocket.py            # Logic WebSocket xử lý gói tin Opus/JSON
└── services/                   # Business Logic & AI Services
    ├── audio_processor.py      # Logic Decode Opus -> PCM & Buffer âm thanh
    ├── openai_service.py       # Tương tác với OpenAI (STT, LLM, TTS)
    └── mcp_controller.py       # Logic xử lý Function Calling (phân tích lệnh phần cứng)
```

## 5. API Endpoints
- `WS /ws/audio` : Endpoint WebSocket chính tiếp nhận âm thanh (Binary) và tín hiệu điều khiển (JSON) từ ESP32.

## 6. Rủi ro & Điểm cần lưu ý (Trade-offs)
- **Độ trễ do Chunking:** Vì OpenAI Whisper API không nhận streaming PCM trực tiếp (nó nhận file), Backend sẽ phải chờ thiết bị nói xong một cụm (nhờ tín hiệu VAD hoặc timeout) để gửi file audio lên phân tích. Điều này sẽ có độ trễ lớn hơn so với Realtime API.
- **Thư viện C++ (Native):** Việc dùng `opuslib` trên Python yêu cầu hệ điều hành máy chủ phải cài đặt thư viện hệ thống `libopus` (trên Ubuntu: `apt install libopus0`).

## 7. Các bước triển khai (Implementation Plan)
1. Khởi tạo cấu trúc dự án FastAPI.
2. Xây dựng module `ConnectionManager` để quản lý WebSocket clients.
3. Viết module `AudioProcessor` để giải mã Opus ra PCM.
4. Tích hợp OpenAI Service (tạo các hàm gọi STT, LLM, TTS cơ bản).
5. Gắn kết logic vào endpoint `/ws/audio` tạo thành một Pipeline hoàn chỉnh.
