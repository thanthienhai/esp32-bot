import io
import wave
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self, api_key: str, llm_model: str = "gpt-4o-mini", tts_model: str = "tts-1"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.llm_model = llm_model
        self.tts_model = tts_model

    async def stt(self, audio_bytes: bytes) -> str:
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_bytes)
        
        wav_io.seek(0)
        wav_io.name = "audio.wav"
        
        try:
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_io,
                language="vi"
            )
            return response.text
        except Exception as e:
            raise e

    async def llm_stream(self, text: str, history: list = None):
        if history is None:
            history = []
        
        messages = [
            {"role": "system", "content": "Bạn là Sophia, một robot trợ lý thông minh người Việt Nam. Hãy trả lời ngắn gọn, lễ phép, thân thiện và luôn dùng Tiếng Việt."},
            *history,
            {"role": "user", "content": text}
        ]
        
        stream = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def tts(self, text: str) -> bytes:
        """
        Gửi văn bản tới OpenAI TTS API và nhận dữ liệu âm thanh.
        """
        response = await self.client.audio.speech.create(
            model=self.tts_model,
            voice="nova",
            input=text,
            response_format="mp3"
        )
        # Sửa lỗi: read() của response trong AsyncOpenAI KHÔNG cần await (nó trả về bytes ngay)
        # Hoặc chính xác hơn trong bản mới: await response.aread() nếu dùng content
        # Cách an toàn nhất là gọi .content trực tiếp (thuộc tính) hoặc .aread() (phương thức async)
        return await response.aread()
