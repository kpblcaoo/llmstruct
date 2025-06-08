from fastapi import APIRouter, Depends
from ..models import ChatRequest, ChatResponse
from ..deps import get_api_key

router = APIRouter()

@router.post("/chat/message", response_model=ChatResponse)
async def chat_message(
    req: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    """Обработчик чата: принимает сообщение, возвращает ответ (заглушка)."""
    return ChatResponse(content=f"Ответ: {req.content}") 