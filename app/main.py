from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="AI Appointment Setter")

@app.get("/health")
async def health():
    return {"ok": True}
