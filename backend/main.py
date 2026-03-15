import uvicorn
from fastapi import FastAPI
from api.websocket import router as websocket_router
from core.config import get_settings

app = FastAPI(title="Sophia AI Backend")

# Kết nối các route WebSocket
app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Sophia AI Backend is Running"}

if __name__ == "__main__":
    settings = get_settings()
    print(f"Starting Sophia AI Backend on {settings.ws_host}:{settings.ws_port}")
    uvicorn.run(
        "main:app", 
        host=settings.ws_host, 
        port=settings.ws_port, 
        reload=True
    )
