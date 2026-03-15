import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from unittest.mock import AsyncMock, patch
from services.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_stt_success():
    with patch("services.openai_service.AsyncOpenAI") as mock_openai_class:
        mock_client = mock_openai_class.return_value
        # Mocking the transcriptions response
        mock_response = AsyncMock()
        mock_response.text = "Xin chào Sophia"
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
        
        service = OpenAIService(api_key="test-key")
        result = await service.stt(b"fake_audio_data")
        
        assert result == "Xin chào Sophia"
        assert mock_client.audio.transcriptions.create.called
