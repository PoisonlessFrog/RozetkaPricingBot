from fastapi import FastAPI, Request
import asyncio
from notifier import notify_user

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    chat_id = data.get("chat_id")
    if message and chat_id:
        await notify_user(chat_id, message)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)