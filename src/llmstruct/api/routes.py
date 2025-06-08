from fastapi import APIRouter, Depends, HTTPException, Request
from .auth import verify_api_key

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/chat/message")
async def chat_message(request: Request, api_key: str = Depends(verify_api_key)):
    data = await request.json()
    user_message = data.get("content")
    if not user_message:
        raise HTTPException(400, "No content provided")
    reply = f"Ответ от бэкенда: {user_message}"
    return {"content": reply} 