import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from core.connection_manager import ConnectionManager

class MockWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent_data = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent_data.append(data)

@pytest.mark.asyncio
async def test_connection_manager():
    manager = ConnectionManager()
    ws = MockWebSocket()
    
    await manager.connect(ws, "client-1")
    assert ws.accepted == True
    assert "client-1" in manager.active_connections
    
    await manager.send_personal_message({"action": "test"}, "client-1")
    assert len(ws.sent_data) == 1
    
    manager.disconnect("client-1")
    assert "client-1" not in manager.active_connections
