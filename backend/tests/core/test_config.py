import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import get_settings

def test_config_loads_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    settings = get_settings()
    assert settings.openai_api_key == "test-key-123"
    assert settings.ws_host == "0.0.0.0"
    assert settings.ws_port == 8000
