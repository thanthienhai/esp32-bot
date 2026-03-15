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
