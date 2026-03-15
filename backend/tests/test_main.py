import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Sophia AI Backend is Running"}

def test_websocket_connect():
    with client.websocket_connect("/ws/audio/test-client") as websocket:
        websocket.send_text("Hello")
        # Just ensure it connects without dropping immediately
        pass
