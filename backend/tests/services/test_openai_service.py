import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_stt_success():
    with patch("services.openai_service.AsyncOpenAI") as mock_openai_class:
        mock_client = mock_openai_class.return_value
        mock_response = AsyncMock()
        mock_response.text = "Xin chào Sophia"
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
        
        service = OpenAIService(api_key="test-key")
        result = await service.stt(b"fake_audio_data")
        
        assert result == "Xin chào Sophia"
        assert mock_client.audio.transcriptions.create.called

@pytest.mark.asyncio
async def test_llm_stream():
    with patch("services.openai_service.AsyncOpenAI") as mock_openai_class:
        mock_client = mock_openai_class.return_value
        
        # Mock stream response
        async def mock_gen():
            # Mock chunk structure from OpenAI
            chunk1 = MagicMock()
            chunk1.choices = [MagicMock()]
            chunk1.choices[0].delta.content = "Chào"
            
            chunk2 = MagicMock()
            chunk2.choices = [MagicMock()]
            chunk2.choices[0].delta.content = " bạn"
            
            yield chunk1
            yield chunk2
            
        mock_client.chat.completions.create = AsyncMock(return_value=mock_gen())
        
        service = OpenAIService(api_key="test-key")
        tokens = []
        async for chunk in service.llm_stream("Chào"):
            tokens.append(chunk)
        
        assert "".join(tokens) == "Chào bạn"
        assert mock_client.chat.completions.create.called
