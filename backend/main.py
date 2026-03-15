from fastapi import FastAPI
from api.websocket import router as websocket_router

app = FastAPI(title="Sophia AI Backend")

app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Sophia Backend Running"}
