#!/usr/bin/env python3
"""
🚀 Объединенный FastAPI сервер для LLMStruct
- Ollama интеграция
- Память пользователей 
- Метрики системы
- Все в одном файле для простоты
"""

import json
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Missing dependencies. Install with: pip install fastapi uvicorn")
    exit(1)

# Инициализация метрик
try:
    from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event, track_task_start, track_task_complete
    METRICS_AVAILABLE = True
    print("📊 Metrics system loaded")
except ImportError:
    METRICS_AVAILABLE = False
    print("⚠️ Metrics system not available")

# Создание FastAPI приложения
app = FastAPI(
    title="LLMStruct Ollama API",
    description="Unified API for LLMStruct with Ollama, Memory and Metrics",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище памяти
USER_MEMORY_FILE = Path("data/user_memory.json")
USER_MEMORY_FILE.parent.mkdir(exist_ok=True)

def load_user_memory() -> Dict[str, List[Dict]]:
    """Загрузка памяти пользователей"""
    if USER_MEMORY_FILE.exists():
        try:
            with open(USER_MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading memory: {e}")
    return {}

def save_user_memory(memory: Dict[str, List[Dict]]):
    """Сохранение памяти пользователей"""
    try:
        with open(USER_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving memory: {e}")

def load_ollama_config():
    """Загрузка конфигурации Ollama"""
    try:
        import toml
        with open("llmstruct.toml", "r") as f:
            config = toml.load(f)
        return config["api"]["ollama_host"]
    except Exception:
        return "http://192.168.88.50:11434"

# Модели данных
class UserMessage(BaseModel):
    user_id: int
    username: str
    message: str
    timestamp: str
    type: str = "user_message"

class OllamaRequest(BaseModel):
    message: str
    context_mode: str = "focused"
    session_id: str = "default"
    model: str = "mistral:latest"
    use_ollama: bool = True

class ChatMessage(BaseModel):
    message: str
    context_mode: str = "focused"
    session_id: str = "default"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_version: str
    metrics_enabled: bool
    ollama_available: bool

# ОСНОВНЫЕ ENDPOINTS

@app.get("/", summary="API Information")
async def root():
    """Информация об API"""
    return {
        "name": "LLMStruct Ollama API",
        "version": "2.0.0",
        "features": {
            "ollama_chat": True,
            "user_memory": True,
            "metrics": METRICS_AVAILABLE,
            "health_checks": True
        },
        "endpoints": {
            "health": "/api/v1/system/health",
            "ollama": "/api/v1/chat/ollama",
            "memory": "/api/v1/memory/*",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/system/health", response_model=HealthResponse)
async def health_check():
    """Health check с проверкой Ollama"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "health_check")
    
    # Проверяем Ollama
    ollama_available = False
    try:
        ollama_host = load_ollama_config()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_host}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                ollama_available = resp.status == 200
    except Exception:
        ollama_available = False
    
    return HealthResponse(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        api_version="2.0.0",
        metrics_enabled=METRICS_AVAILABLE,
        ollama_available=ollama_available
    )

@app.get("/api/v1/system/status")
async def system_status():
    """Детальный статус системы"""
    task_id = f"api_status_{int(time.time())}"
    
    if METRICS_AVAILABLE:
        track_task_start(task_id, "api_system_status")
        track_workflow_event("api_call", "system_status")
    
    try:
        # Статус struct.json
        struct_file = Path("struct.json")
        struct_status = "missing"
        struct_size = 0
        struct_modified = None
        
        if struct_file.exists():
            stat = struct_file.stat()
            struct_size = stat.st_size
            struct_modified = time.ctime(stat.st_mtime)
            age_hours = (time.time() - stat.st_mtime) / 3600
            
            if age_hours < 1:
                struct_status = "fresh"
            elif age_hours < 6:
                struct_status = "recent"
            else:
                struct_status = "outdated"
        
        # Статус памяти
        memory = load_user_memory()
        memory_stats = {
            "total_users": len(memory),
            "total_messages": sum(len(messages) for messages in memory.values()),
            "memory_file_exists": USER_MEMORY_FILE.exists()
        }
        
        # Статус Ollama
        ollama_status = {"available": False, "models": []}
        try:
            ollama_host = load_ollama_config()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ollama_host}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ollama_status = {
                            "available": True,
                            "host": ollama_host,
                            "models": [model["name"] for model in data.get("models", [])]
                        }
        except Exception as e:
            ollama_status["error"] = str(e)
        
        # Метрики
        metrics_summary = None
        if METRICS_AVAILABLE:
            try:
                tracker = get_metrics_tracker()
                metrics_summary = tracker.get_session_summary()
                track_task_complete(task_id, "success")
            except Exception as e:
                track_task_complete(task_id, "failed", str(e))
        
        return {
            "system": {
                "status": "running",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_version": "2.0.0"
            },
            "struct_json": {
                "status": struct_status,
                "size_bytes": struct_size,
                "last_modified": struct_modified
            },
            "ollama": ollama_status,
            "memory": memory_stats,
            "metrics": metrics_summary if METRICS_AVAILABLE else {"enabled": False},
            "features": {
                "chat": True,
                "ollama_integration": ollama_status["available"],
                "user_memory": True,
                "metrics": METRICS_AVAILABLE,
                "struct_analysis": struct_file.exists()
            }
        }
        
    except Exception as e:
        if METRICS_AVAILABLE:
            track_task_complete(task_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# OLLAMA ENDPOINTS

@app.post("/api/v1/chat/ollama")
async def chat_with_ollama(request: OllamaRequest):
    """Чат с Ollama"""
    task_id = f"ollama_chat_{int(time.time())}"
    
    if METRICS_AVAILABLE:
        track_task_start(task_id, "ollama_chat")
        track_workflow_event("api_call", "ollama_chat")
    
    try:
        ollama_host = load_ollama_config()
        
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
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_text = data.get('response', 'Нет ответа от Ollama')
                    
                    # Подсчитываем токены
                    input_tokens = len(request.message.split())
                    output_tokens = len(response_text.split())
                    total_tokens = input_tokens + output_tokens
                    
                    if METRICS_AVAILABLE:
                        tracker = get_metrics_tracker()
                        tracker.track_token_usage("ollama", request.model, input_tokens, output_tokens)
                        track_task_complete(task_id, "success")
                    
                    return {
                        "response": response_text,
                        "model": request.model,
                        "session_id": request.session_id,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "tokens_used": total_tokens,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "ollama_host": ollama_host
                    }
                else:
                    error_text = await resp.text()
                    if METRICS_AVAILABLE:
                        track_task_complete(task_id, "failed", f"Ollama HTTP {resp.status}")
                    raise HTTPException(
                        status_code=resp.status,
                        detail=f"Ollama error: {error_text}"
                    )
        
    except asyncio.TimeoutError:
        if METRICS_AVAILABLE:
            track_task_complete(task_id, "failed", "timeout")
        raise HTTPException(status_code=408, detail="Ollama timeout")
    except Exception as e:
        if METRICS_AVAILABLE:
            track_task_complete(task_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.get("/api/v1/ollama/models")
async def get_ollama_models():
    """Получение списка доступных моделей Ollama"""
    try:
        ollama_host = load_ollama_config()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_host}/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = []
                    for model in data.get("models", []):
                        models.append({
                            "name": model["name"],
                            "size": model["size"],
                            "modified": model["modified_at"],
                            "digest": model["digest"][:12] + "...",
                            "details": model.get("details", {})
                        })
                    
                    return {
                        "ollama_host": ollama_host,
                        "models_count": len(models),
                        "models": models
                    }
                else:
                    raise HTTPException(status_code=resp.status, detail="Ollama не отвечает")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения моделей: {str(e)}")

# MEMORY ENDPOINTS

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
        
        if METRICS_AVAILABLE:
            track_workflow_event("memory_save", f"user_{message.user_id}")
        
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
        recent_messages = messages[-limit:] if messages else []
        
        if METRICS_AVAILABLE:
            track_workflow_event("memory_read", f"user_{user_id}")
        
        return {
            "user_id": user_id,
            "total_messages": len(messages),
            "returned_messages": len(recent_messages),
            "messages": recent_messages
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
        
        if METRICS_AVAILABLE:
            track_workflow_event("memory_clear", f"user_{user_id}")
        
        return {
            "status": "cleared",
            "user_id": user_id,
            "deleted_messages": message_count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FILE READING ENDPOINTS

@app.get("/api/v1/files/read")
async def read_project_file(
    path: str = Query(..., description="Путь к файлу относительно корня проекта"),
    lines: int = Query(0, description="Количество строк для чтения (0 = весь файл)"),
    start_line: int = Query(1, description="Начальная строка для чтения")
):
    """Чтение файлов проекта"""
    task_id = f"file_read_{int(time.time())}"
    
    if METRICS_AVAILABLE:
        track_task_start(task_id, "file_read")
        track_workflow_event("api_call", "file_read")
    
    try:
        # Безопасность: разрешаем только определенные файлы
        allowed_files = {
            "README.md": Path("README.md"),
            "struct.json": Path("struct.json"),
            "requirements.txt": Path("requirements.txt"),
            "pyproject.toml": Path("pyproject.toml"),
            ".cursorrules": Path(".cursorrules")
        }
        
        if path not in allowed_files:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", f"File not allowed: {path}")
            raise HTTPException(status_code=403, detail=f"Файл {path} не разрешен для чтения")
        
        file_path = allowed_files[path]
        
        if not file_path.exists():
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", f"File not found: {path}")
            raise HTTPException(status_code=404, detail=f"Файл {path} не найден")
        
        # Читаем файл
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if lines > 0:
                    # Читаем определенное количество строк
                    all_lines = f.readlines()
                    if start_line > len(all_lines):
                        content_lines = []
                    else:
                        end_line = min(start_line + lines - 1, len(all_lines))
                        content_lines = all_lines[start_line-1:end_line]
                    content = ''.join(content_lines)
                    total_lines = len(all_lines)
                    read_lines = len(content_lines)
                else:
                    # Читаем весь файл
                    content = f.read()
                    content_lines = content.split('\n')
                    total_lines = len(content_lines)
                    read_lines = total_lines
        except UnicodeDecodeError:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", "Unicode decode error")
            raise HTTPException(status_code=400, detail="Не удается прочитать файл (проблема кодировки)")
        
        # Информация о файле
        file_stat = file_path.stat()
        file_info = {
            "size_bytes": file_stat.st_size,
            "modified": time.ctime(file_stat.st_mtime),
            "total_lines": total_lines,
            "read_lines": read_lines,
            "start_line": start_line if lines > 0 else 1,
            "encoding": "utf-8"
        }
        
        if METRICS_AVAILABLE:
            track_task_complete(task_id, "success")
        
        return {
            "path": path,
            "content": content,
            "file_info": file_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if METRICS_AVAILABLE:
            track_task_complete(task_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")

@app.get("/api/v1/files/list")
async def list_available_files():
    """Список доступных для чтения файлов"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "file_list")
    
    files_info = []
    allowed_files = ["README.md", "struct.json", "requirements.txt", "pyproject.toml", ".cursorrules"]
    
    for filename in allowed_files:
        file_path = Path(filename)
        if file_path.exists():
            file_stat = file_path.stat()
            files_info.append({
                "name": filename,
                "exists": True,
                "size_bytes": file_stat.st_size,
                "modified": time.ctime(file_stat.st_mtime),
                "readable": True
            })
        else:
            files_info.append({
                "name": filename,
                "exists": False,
                "readable": False
            })
    
    return {
        "available_files": files_info,
        "total_files": len(files_info),
        "existing_files": len([f for f in files_info if f["exists"]]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# STARTUP/SHUTDOWN EVENTS

@app.on_event("startup")
async def startup_event():
    """События при запуске"""
    print("🚀 LLMStruct Ollama API Starting...")
    if METRICS_AVAILABLE:
        tracker = get_metrics_tracker()
        track_workflow_event("api_startup")
        print(f"📊 Metrics session: {tracker.session_file.stem}")
    print("✅ API Ready")

@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке"""
    print("🛑 LLMStruct Ollama API Shutting Down...")
    if METRICS_AVAILABLE:
        track_workflow_event("api_shutdown")
        tracker = get_metrics_tracker()
        tracker.save_session()
        print("📊 Metrics saved")
    print("✅ Shutdown Complete")

if __name__ == "__main__":
    print("🚀 Starting LLMStruct Ollama API server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/system/health")
    print("🤖 Ollama Chat: http://localhost:8000/api/v1/chat/ollama")
    print("🧠 Memory Stats: http://localhost:8000/api/v1/memory/stats")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 