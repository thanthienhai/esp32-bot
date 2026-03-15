import json

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "turn_on_led",
            "description": "Bật đèn LED trên thiết bị",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {"type": "string", "description": "Màu của đèn LED (ví dụ: red, blue)"}
                },
                "required": ["color"]
            }
        }
    }
]

def process_function_call(call_data: dict) -> dict:
    name = call_data.get("name")
    args_str = call_data.get("arguments", "{}")
    
    try:
        args = json.loads(args_str)
    except:
        args = {}
        
    if name == "turn_on_led":
        return {"action": "turn_on_led", **args}
        
    return {"error": "Unknown function"}
