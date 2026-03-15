import io
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def stt(self, audio_bytes: bytes) -> str:
        """
        Gửi dữ liệu âm thanh tới OpenAI Whisper API.
        Dữ liệu được bọc trong BytesIO với tên file 'audio.wav'.
        """
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "audio.wav"
        
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language="vi"
        )
        return response.text

    async def llm_stream(self, text: str, history: list = None):
        """
        Gửi văn bản tới OpenAI LLM và nhận luồng phản hồi (streaming).
        """
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

    async def tts(self, text: str) -> bytes:
        """
        Gửi văn bản tới OpenAI TTS API và nhận dữ liệu âm thanh.
        Giọng nói mặc định: nova.
        """
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            response_format="mp3"
        )
        return await response.read()
