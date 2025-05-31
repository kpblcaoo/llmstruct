#!/usr/bin/env python3
"""
🤖 Enhanced Bot API Server
FastAPI сервер с интеграцией файловых операций бота
"""

import json
import time
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ Missing dependencies. Install with: pip install fastapi uvicorn")
    exit(1)

# Импорт модулей бота
try:
    from bot_file_operations import BotFileOperations
    from struct_cache_manager import StructCacheManager
    BOT_MODULES_AVAILABLE = True
    print("🤖 Bot modules loaded")
except ImportError:
    BOT_MODULES_AVAILABLE = False
    print("⚠️ Bot modules not available")

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
    title="LLMStruct Bot API",
    description="Enhanced API for LLMStruct with Bot File Operations",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные переменные
file_ops = None
cache_manager = None

def get_file_ops():
    """Lazy loading файловых операций"""
    global file_ops
    if file_ops is None and BOT_MODULES_AVAILABLE:
        file_ops = BotFileOperations()
    return file_ops

def get_cache_manager():
    """Lazy loading кеш менеджера"""
    global cache_manager
    if cache_manager is None and BOT_MODULES_AVAILABLE:
        cache_manager = StructCacheManager()
    return cache_manager

# Модели данных
class FileWriteRequest(BaseModel):
    file_path: str
    content: str
    mode: str = "w"

class FileEditRequest(BaseModel):
    file_path: str
    operation: Dict[str, Any]

class ChatMessage(BaseModel):
    message: str
    context_mode: str = "focused"
    session_id: str = "default"

# ОСНОВНЫЕ ENDPOINTS

@app.get("/", summary="Bot API Information")
async def root():
    """Информация об API"""
    return {
        "name": "LLMStruct Bot API",
        "version": "3.0.0",
        "features": {
            "file_operations": BOT_MODULES_AVAILABLE,
            "struct_caching": BOT_MODULES_AVAILABLE,
            "metrics": METRICS_AVAILABLE,
            "ollama_integration": True
        },
        "endpoints": {
            "health": "/health",
            "files": "/api/v1/files/*",
            "struct": "/api/v1/struct/*",
            "workspace": "/api/v1/workspace/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "health_check")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "3.0.0",
        "bot_modules": BOT_MODULES_AVAILABLE,
        "metrics_enabled": METRICS_AVAILABLE
    }

# FILE OPERATIONS ENDPOINTS

@app.get("/api/v1/files/list")
async def list_files(path: str = Query(".", description="Directory path to list")):
    """Список файлов в рабочей директории"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "files_list")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    if ops is None:
        raise HTTPException(status_code=503, detail="Could not initialize file operations")
    
    result = ops.list_files(path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/api/v1/files/read")
async def read_file(file_path: str = Query(..., description="File path to read")):
    """Чтение файла"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "file_read")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    if ops is None:
        raise HTTPException(status_code=503, detail="Could not initialize file operations")
    
    result = ops.read_file(file_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/api/v1/files/write")
async def write_file(request: FileWriteRequest):
    """Запись файла"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "file_write")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    if ops is None:
        raise HTTPException(status_code=503, detail="Could not initialize file operations")
    
    result = ops.write_file(request.file_path, request.content, request.mode)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/api/v1/files/edit")
async def edit_file(request: FileEditRequest):
    """Редактирование файла"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "file_edit")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    if ops is None:
        raise HTTPException(status_code=503, detail="Could not initialize file operations")
    
    result = ops.edit_file(request.file_path, request.operation)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/api/v1/files/mkdir")
async def create_directory(dir_path: str = Query(..., description="Directory path to create")):
    """Создание директории"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "mkdir")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    result = ops.create_directory(dir_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.delete("/api/v1/files/delete")
async def delete_file(file_path: str = Query(..., description="File/directory path to delete")):
    """Удаление файла или директории"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "file_delete")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    result = ops.delete_file(file_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# STRUCT.JSON OPERATIONS

@app.get("/api/v1/struct/search")
async def search_struct(
    query: str = Query(..., description="Search query"),
    search_type: str = Query("all", description="Search type: all, modules, functions, classes")
):
    """Поиск в struct.json с кешированием"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "struct_search")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    result = ops.search_struct(query, search_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/api/v1/struct/stats")
async def get_struct_stats():
    """Статистика struct.json кеша"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "struct_stats")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    cache = get_cache_manager()
    result = cache.get_cache_stats()
    return result

@app.post("/api/v1/struct/invalidate")
async def invalidate_struct_cache():
    """Инвалидация кеша struct.json"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "cache_invalidate")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    cache = get_cache_manager()
    cache.invalidate_cache()
    return {"status": "cache_invalidated", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/struct/rebuild")
async def rebuild_struct_cache():
    """Перестроение кеша struct.json"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "cache_rebuild")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    cache = get_cache_manager()
    success = cache.build_cache()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to rebuild cache")
    
    stats = cache.get_cache_stats()
    return {
        "status": "cache_rebuilt",
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }

# WORKSPACE OPERATIONS

@app.get("/api/v1/workspace/status")
async def get_workspace_status():
    """Статус рабочего пространства"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "workspace_status")
    
    if not BOT_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot modules not available")
    
    ops = get_file_ops()
    result = ops.get_workspace_status()
    return result

# CLAUDE COMMUNICATION ENDPOINT

@app.post("/api/v1/claude/message")
async def send_message_to_claude(message: ChatMessage):
    """Отправка сообщения Claude через API (симуляция)"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "claude_message")
    
    # Симуляция ответа от Claude
    return {
        "status": "message_queued",
        "message_id": f"msg_{int(time.time())}",
        "session_id": message.session_id,
        "context_mode": message.context_mode,
        "timestamp": datetime.now().isoformat(),
        "note": "This is a simulation endpoint for Claude communication"
    }

# TEST ENDPOINTS

@app.get("/api/v1/test/full")
async def run_full_test():
    """Полный тест всех функций бота"""
    if METRICS_AVAILABLE:
        track_workflow_event("api_call", "full_test")
    
    if not BOT_MODULES_AVAILABLE:
        return {"error": "Bot modules not available"}
    
    results = {}
    
    # Тест файловых операций
    ops = get_file_ops()
    if ops:
        test_content = "Test file created by API\nTimestamp: " + datetime.now().isoformat()
        write_result = ops.write_file("api_test.txt", test_content)
        read_result = ops.read_file("api_test.txt")
        
        results["file_operations"] = {
            "write": write_result,
            "read": {"success": "error" not in read_result}
        }
    
    # Тест кеша
    cache = get_cache_manager()
    if cache:
        stats = cache.get_cache_stats()
        search_result = cache.smart_search("test", "functions")
        
        results["cache_operations"] = {
            "stats": stats,
            "search_results": len(search_result.get("functions", []))
        }
    
    return {
        "test_status": "completed",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

# STARTUP/SHUTDOWN EVENTS

@app.on_event("startup")
async def startup_event():
    """События при запуске"""
    print("🤖 LLMStruct Bot API Starting...")
    if METRICS_AVAILABLE:
        track_workflow_event("api_startup")
    if BOT_MODULES_AVAILABLE:
        print("✅ Bot modules ready")
    print("✅ Bot API Ready")

@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке"""
    print("🛑 LLMStruct Bot API Shutting Down...")
    if METRICS_AVAILABLE:
        track_workflow_event("api_shutdown")
    print("✅ Shutdown Complete")

if __name__ == "__main__":
    print("🤖 Starting LLMStruct Bot API server...")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("📁 File Operations: http://localhost:8001/api/v1/files/*")
    print("🗃️ Struct Search: http://localhost:8001/api/v1/struct/search")
    print("🏢 Workspace Status: http://localhost:8001/api/v1/workspace/status")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    ) 