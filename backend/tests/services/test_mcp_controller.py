import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.mcp_controller import process_function_call

def test_process_function_call_led():
    call_data = {"name": "turn_on_led", "arguments": '{"color": "red"}'}
    result = process_function_call(call_data)
    assert result == {"action": "turn_on_led", "color": "red"}

def test_process_function_call_unknown():
    call_data = {"name": "unknown", "arguments": '{}'}
    result = process_function_call(call_data)
    assert result == {"error": "Unknown function"}
