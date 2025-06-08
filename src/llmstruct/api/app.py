from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, health

app = FastAPI(
    title="LLMStruct API",
    version="0.1.0",
    description="API для чата и интеграции с llmstruct"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена — явно!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["system"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"]) 