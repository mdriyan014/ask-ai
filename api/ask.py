import os
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()

CHATANYWHERE_URL = "https://api.chatanywhere.tech/v1/chat/completions"
CHATANYWHERE_API_KEY = os.getenv("CHATANYWHERE_API_KEY")

ACCESS_KEY = "dark"

@app.get("/")
def home():
    return {
        "status": True,
        "message": "AI Running",
        "usage": "/api/ask?key=dark&ask=Hello"
    }

@app.get("/api/ask")
async def ask_ai(
    key: str = Query(...),
    ask: str = Query(...)
):
    if key != ACCESS_KEY:
        return JSONResponse({"status": False, "error": "Invalid access key"}, status_code=403)

    if not CHATANYWHERE_API_KEY:
        return {"status": False, "error": "API key not configured"}

    headers = {
        "Authorization": f"Bearer {CHATANYWHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-ca",
        "messages": [{"role": "user", "content": ask}]
    }

    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.post(CHATANYWHERE_URL, headers=headers, json=payload)

    data = r.json()

    if "choices" not in data:
        return {"status": False, "error": data}

    return {
        "status": True,
        "answer": data["choices"][0]["message"]["content"]
    }
