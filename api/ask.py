import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from time import time

app = FastAPI()

# 🔥 নিজের নতুন API key বসাও (পুরানটা revoke করো)
API_KEY = "sk-sRcjuojZqugywcfj8IY8qBgGZgEr7KWNVydiZt5QMCAY2xuf"

CHATANYWHERE_URL = "https://api.chatanywhere.tech/v1/chat/completions"
ACCESS_KEY = "dark"

# ===== Memory System =====
MAX_MEMORY = 10
memory = []

# ===== Rate Limit =====
RATE_LIMIT = 15
RATE_WINDOW = 60
request_log = []

SYSTEM_PROMPT = """
You are a smart and direct AI assistant.

Creator:
Name: Riyan
Country: Bangladesh
Status: Class 10 Student
Does coding sometimes.

Rules:
- Answer short and clear unless user asks detailed.
- Never share private location, school, address.
- If asked about real-time activity, say you don’t have live access.
"""

# =========================

def check_rate():
    now = int(time())
    global request_log
    request_log = [t for t in request_log if t > now - RATE_WINDOW]

    if len(request_log) >= RATE_LIMIT:
        return False

    request_log.append(now)
    return True


@app.get("/")
async def home():
    return {
        "status": True,
        "message": "Riyan AI Running",
        "usage": "/api/ask?key=dark&ask=hello&mode=short"
    }


@app.get("/api/ask")
async def ask_ai(
    key: str = Query(...),
    ask: str = Query(...),
    mode: str = Query("short")  # short / detailed
):
    if key != ACCESS_KEY:
        return JSONResponse(
            {"status": False, "error": "Invalid access key"},
            status_code=403
        )

    if not check_rate():
        return {"status": False, "error": "Rate limit exceeded"}

    global memory

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in memory:
        messages.append(m)

    if mode == "detailed":
        ask = ask + "\nExplain slightly detailed."
    else:
        ask = ask + "\nAnswer very short."

    messages.append({"role": "user", "content": ask})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-ca",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 300
    }

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                CHATANYWHERE_URL,
                headers=headers,
                json=payload
            )

        data = response.json()

        if "choices" not in data:
            return {"status": False, "error": data}

        answer = data["choices"][0]["message"]["content"].strip()

        # Save memory
        memory.append({"role": "user", "content": ask})
        memory.append({"role": "assistant", "content": answer})
        memory = memory[-MAX_MEMORY:]

        return {
            "status": True,
            "mode": mode,
            "memory_size": len(memory),
            "answer": answer
        }

    except Exception as e:
        return {"status": False, "error": str(e)}
