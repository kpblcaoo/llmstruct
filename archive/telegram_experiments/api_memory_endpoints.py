#!/usr/bin/env python3
"""
API Endpoints для памяти Telegram бота
Интеграция с FastAPI для кеша сообщений пользователей
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from fastapi import FastAPI, HTTPException, Query
    from pydantic import BaseModel
except ImportError:
    print("❌ Missing FastAPI dependencies")
    exit(1)

# Модели данных для памяти
class UserMessage(BaseModel):
    user_id: int
    username: str
    message: str
    timestamp: str
    type: str = "user_message"

class MemoryQuery(BaseModel):
    user_id: int
    query: str
    context_limit: int = 10

class OllamaRequest(BaseModel):
    message: str
    context_mode: str = "focused"
    session_id: str = "default"
    model: str = "mistral:latest"
    use_ollama: bool = True

# Хранилище памяти (в production - база данных)
USER_MEMORY_FILE = Path("data/user_memory.json")
USER_MEMORY_FILE.parent.mkdir(exist_ok=True)

def load_user_memory() -> Dict[str, List[Dict]]:
    """Загрузка памяти пользователей из файла"""
    if USER_MEMORY_FILE.exists():
        try:
            with open(USER_MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading memory: {e}")
    return {}

def save_user_memory(memory: Dict[str, List[Dict]]):
    """Сохранение памяти пользователей в файл"""
    try:
        with open(USER_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving memory: {e}")

def add_memory_endpoints(app: FastAPI):
    """Добавление endpoints памяти к FastAPI приложению"""
    
    @app.post("/api/v1/memory/save")
    async def save_user_message(message: UserMessage):
        """Сохранение сообщения пользователя"""
        try:
            memory = load_user_memory()
            user_key = str(message.user_id)
            
            if user_key not in memory:
                memory[user_key] = []
            
            # Добавляем сообщение
            memory[user_key].append({
                "username": message.username,
                "message": message.message,
                "timestamp": message.timestamp,
                "type": message.type
            })
            
            # Ограничиваем историю (последние 100 сообщений)
            if len(memory[user_key]) > 100:
                memory[user_key] = memory[user_key][-100:]
            
            save_user_memory(memory)
            
            return {
                "status": "saved",
                "user_id": message.user_id,
                "message_count": len(memory[user_key]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/memory/history/{user_id}")
    async def get_user_history(
        user_id: int, 
        limit: int = Query(10, description="Количество сообщений")
    ):
        """Получение истории сообщений пользователя"""
        try:
            memory = load_user_memory()
            user_key = str(user_id)
            
            messages = memory.get(user_key, [])
            
            # Возвращаем последние N сообщений
            recent_messages = messages[-limit:] if messages else []
            
            return {
                "user_id": user_id,
                "total_messages": len(messages),
                "returned_messages": len(recent_messages),
                "messages": recent_messages
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/memory/search")
    async def search_user_memory(query: MemoryQuery):
        """Поиск в памяти пользователя"""
        try:
            memory = load_user_memory()
            user_key = str(query.user_id)
            
            messages = memory.get(user_key, [])
            
            # Простой поиск по содержимому
            found_messages = []
            search_term = query.query.lower()
            
            for msg in messages:
                if search_term in msg.get('message', '').lower():
                    found_messages.append(msg)
            
            # Ограничиваем результат
            found_messages = found_messages[-query.context_limit:]
            
            return {
                "user_id": query.user_id,
                "search_query": query.query,
                "found_count": len(found_messages),
                "messages": found_messages
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/chat/ollama")
    async def chat_with_ollama(request: OllamaRequest):
        """Чат с Ollama через API"""
        try:
            import aiohttp
            import asyncio
            
            # Загружаем конфигурацию Ollama
            try:
                import toml
                with open("llmstruct.toml", "r") as f:
                    config = toml.load(f)
                ollama_host = config["api"]["ollama_host"]
            except Exception:
                ollama_host = "http://192.168.88.50:11434"
            
            # Формируем запрос к Ollama
            ollama_payload = {
                "model": request.model,
                "prompt": request.message,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{ollama_host}/api/generate",
                    json=ollama_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data.get('response', 'Нет ответа от Ollama')
                        
                        # Подсчитываем токены (приблизительно)
                        input_tokens = len(request.message.split())
                        output_tokens = len(response_text.split())
                        total_tokens = input_tokens + output_tokens
                        
                        return {
                            "response": response_text,
                            "model": request.model,
                            "session_id": request.session_id,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "tokens_used": total_tokens,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens
                        }
                    else:
                        error_text = await resp.text()
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Ollama error: {error_text}"
                        )
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Ollama timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")
    
    @app.delete("/api/v1/memory/clear/{user_id}")
    async def clear_user_memory(user_id: int):
        """Очистка памяти пользователя"""
        try:
            memory = load_user_memory()
            user_key = str(user_id)
            
            message_count = len(memory.get(user_key, []))
            
            if user_key in memory:
                del memory[user_key]
                save_user_memory(memory)
            
            return {
                "status": "cleared",
                "user_id": user_id,
                "deleted_messages": message_count,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/memory/stats")
    async def memory_stats():
        """Статистика памяти"""
        try:
            memory = load_user_memory()
            
            total_users = len(memory)
            total_messages = sum(len(messages) for messages in memory.values())
            
            # Статистика по пользователям
            user_stats = []
            for user_id, messages in memory.items():
                if messages:
                    last_message = messages[-1]
                    user_stats.append({
                        "user_id": int(user_id),
                        "message_count": len(messages),
                        "last_activity": last_message.get('timestamp', 'N/A'),
                        "username": last_message.get('username', 'unknown')
                    })
            
            # Сортируем по активности
            user_stats.sort(key=lambda x: x['last_activity'], reverse=True)
            
            return {
                "total_users": total_users,
                "total_messages": total_messages,
                "memory_file_size": USER_MEMORY_FILE.stat().st_size if USER_MEMORY_FILE.exists() else 0,
                "last_updated": time.ctime(USER_MEMORY_FILE.stat().st_mtime) if USER_MEMORY_FILE.exists() else None,
                "user_stats": user_stats[:10]  # Топ 10 активных пользователей
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🧠 Memory API endpoints готовы для интеграции")
    print("Добавьте в ваш main FastAPI:")
    print("from api_memory_endpoints import add_memory_endpoints")
    print("add_memory_endpoints(app)") 