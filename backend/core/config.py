from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_llm_model: str = "gpt-4o-mini"  # Model tiết kiệm nhất
    openai_tts_model: str = "tts-1"        # Model tiêu chuẩn (rẻ hơn tts-1-hd)
    ws_host: str = "0.0.0.0"
    ws_port: int = 8000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
