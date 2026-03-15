# Thiết kế Tích hợp OpenAI cho Robot Sophia (FastAPI Backend)

**Ngày:** 2026-03-15
**Dự án:** Xiaozhi ESP32 Vietnam (Sophia) - AI Backend Integration

## 1. Mục tiêu
Nâng cấp AI Backend từ bộ khung cơ bản lên hệ thống hoàn chỉnh có khả năng:
- Nhận dạng giọng nói (STT) Tiếng Việt thời gian thực.
- Xử lý ngôn ngữ tự nhiên (LLM) với nhân cách "Sophia".
- Tổng hợp giọng nói (TTS) chất lượng cao bằng Tiếng Việt và stream xuống thiết bị với độ trễ tối thiểu.
- Hỗ trợ điều khiển phần cứng qua MCP (Function Calling).

## 2. Các thành phần chính (Components)

### 2.1. STT Service (Speech-to-Text)
- **Công nghệ:** OpenAI Whisper API.
- **Cơ chế:**
  - Gom buffer PCM từ `AudioProcessor`.
  - Khi nhận tín hiệu VAD (Silence detected) hoặc gói tin ngắt luồng từ ESP32, tiến hành đóng gói buffer thành tệp `.wav` (in-memory) và gửi tới Whisper API.
  - Kết quả là văn bản Tiếng Việt (String).

### 2.2. LLM Service (Large Language Model)
- **Công nghệ:** OpenAI GPT-4o-mini.
- **Cấu hình:**
  - **System Prompt:** "Bạn là Sophia, một robot trợ lý thông minh người Việt Nam. Hãy trả lời ngắn gọn, lễ phép, thân thiện và luôn dùng Tiếng Việt. Bạn có khả năng điều khiển các thiết bị phần cứng qua MCP (Model Context Protocol)."
  - **Streaming:** Bật chế độ `stream=True` để nhận token ngay khi model đang suy nghĩ.
  - **Tools (MCP):** Nhúng danh sách hàm điều khiển thiết bị (VD: `turn_on_led`) vào cấu hình gọi model.

### 2.3. TTS Service (Text-to-Speech)
- **Công nghệ:** OpenAI TTS API (Model: `tts-1`, Voice: `nova`).
- **Cơ chế Sentence-Streaming:**
  - Nhận luồng token từ LLM.
  - Sử dụng Regex để phát hiện kết thúc câu (dựa trên dấu `.`, `!`, `?`, `\n`).
  - Mỗi câu hoàn chỉnh sẽ được đẩy vào TTS Queue để sinh âm thanh ngay lập tức (không đợi LLM xong cả đoạn văn).
  - Kết quả âm thanh sẽ được mã hóa lại thành **Opus** (sử dụng `opuslib`) trước khi gửi xuống WebSocket (Binary).

## 3. Quy trình xử lý luồng (Sequence Flow)

1. **ESP32** → (Opus frames) → **Backend (WebSocket)**.
2. **Backend** → Decode Opus → Buffer PCM → Phát hiện khoảng lặng (Silence).
3. **Backend** → Whisper API → Văn bản.
4. **Backend** → GPT-4o-mini (Stream) → Tokens.
5. **Backend** → Tách câu (Sentence Splitting).
6. **Backend** → OpenAI TTS (Nova) → Âm thanh câu.
7. **Backend** → Encode Opus → Gửi Binary xuống **ESP32** để phát loa.
8. (Nếu có Function Call) → **Backend** → JSON Command xuống **ESP32**.

## 4. Cấu trúc cập nhật trong `services/openai_service.py`

```python
class OpenAIService:
    async def stt(self, audio_data: bytes) -> str:
        # Gửi tới Whisper
        pass

    async def llm_stream(self, text: str, history: list):
        # Trả về Generator các token/sentences
        pass

    async def tts_stream(self, text: str):
        # Trả về Audio bytes (Opus)
        pass
```

## 5. Rủi ro & Giải pháp
- **Độ trễ mạng:** Sử dụng Sentence-level streaming để bắt đầu phát âm thanh ngay từ câu đầu tiên của câu trả lời.
- **Đồng bộ hóa:** Cần cơ chế dọn dẹp (Clear) hàng đợi âm thanh nếu người dùng ngắt lời (Interrupt) Sophia.

## 6. Kiểm thử (Testing)
- Unit test cho việc tách câu (Sentence splitting).
- Mock OpenAI API để kiểm tra luồng logic mà không tốn chi phí API thật.
- Kiểm tra độ nén và chất lượng của Opus Encoder.
