#!/usr/bin/env python3
"""
Ollama Chat Bot использующий FastAPI API вместо CLI
Более эффективная интеграция с существующей API инфраструктурой
"""

import os
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import signal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ollama_api_bot.log', encoding='utf-8')
    ]
)

@dataclass
class ChatMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    model_used: str = "unknown"
    tokens_used: Optional[int] = None

@dataclass
class ChatSession:
    session_id: str
    chat_id: int
    user_id: int
    user_name: str
    started_at: str
    last_activity: str
    messages: List[ChatMessage]
    preferred_model: str = "ollama"
    total_tokens: int = 0

class APIClient:
    """Клиент для работы с FastAPI сервером"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья API"""
        async with self.session.get(f"{self.api_base_url}/api/v1/system/health") as response:
            return await response.json()
    
    async def system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        async with self.session.get(f"{self.api_base_url}/api/v1/system/status") as response:
            return await response.json()
    
    async def chat_message(self, message: str, context_mode: str = "focused", session_id: str = "default") -> Dict[str, Any]:
        """Отправка сообщения в чат через API"""
        payload = {
            "message": message,
            "context_mode": context_mode,
            "session_id": session_id
        }
        async with self.session.post(f"{self.api_base_url}/api/v1/chat/message", json=payload) as response:
            return await response.json()
    
    async def execute_cli_command(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Выполнение CLI команды через API"""
        payload = {
            "command": command,
            "args": args or {}
        }
        async with self.session.post(f"{self.api_base_url}/api/v1/cli/execute", json=payload) as response:
            return await response.json()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        async with self.session.get(f"{self.api_base_url}/api/v1/metrics") as response:
            return await response.json()

class ModelManager:
    """Менеджер LLM моделей с API интеграцией"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.ollama_url = "http://localhost:11434"
        
    async def chat_with_ollama(self, messages: List[Dict], model: str = "llama3.2") -> Optional[str]:
        """Общение с Ollama через прямой API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False
                }
                async with session.post(f"{self.ollama_url}/api/chat", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["message"]["content"]
                    else:
                        logging.error(f"Ollama API error: {response.status}")
                        return None
        except Exception as e:
            logging.error(f"Ollama connection error: {e}")
            return None
    
    async def chat_with_api_fallback(self, message: str, session_id: str) -> str:
        """Fallback через FastAPI чат"""
        try:
            result = await self.api_client.chat_message(message, "focused", session_id)
            return result.get("response", "API fallback response not available")
        except Exception as e:
            logging.error(f"API fallback error: {e}")
            return "⚠️ Извините, все системы временно недоступны"

class FileManager:
    """Менеджер файлов через API"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.project_root = "/home/sma/projects/llmstruct/llmstruct"
    
    async def read_file(self, file_path: str, max_lines: int = 100) -> str:
        """Чтение файла через API команды"""
        try:
            # Можно использовать CLI через API
            args = {"path": file_path, "lines": max_lines}
            result = await self.api_client.execute_cli_command("query", args)
            return result.get("stdout", "Файл не найден")
        except Exception as e:
            return f"❌ Ошибка чтения файла: {e}"
    
    async def get_system_status(self) -> str:
        """Получение статуса системы"""
        try:
            status = await self.api_client.system_status()
            return f"""📊 **Статус системы LLMStruct**

🟢 **API**: {status['system']['status']}
📁 **struct.json**: {status['struct_json']['status']} ({status['struct_json']['size_bytes']} байт)
📊 **Метрики**: {'включены' if status['features']['metrics'] else 'отключены'}
🔧 **Функции**: {', '.join([k for k, v in status['features'].items() if v])}

⏰ Обновлено: {status['system']['timestamp']}"""
        except Exception as e:
            return f"❌ Ошибка получения статуса: {e}"

class MemoryManager:
    """Менеджер памяти с API интеграцией"""
    
    def __init__(self, storage_dir: str = "data/ollama_api_chat", api_client: APIClient = None):
        self.storage_dir = storage_dir
        self.api_client = api_client
        self.sessions_file = f"{storage_dir}/sessions.json"
        self.sessions: Dict[str, ChatSession] = {}
        
        # Создание директории
        os.makedirs(storage_dir, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Загрузка сессий из файла"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = ChatSession(**session_data)
                        # Восстановление объектов сообщений
                        session.messages = [ChatMessage(**msg) for msg in session.messages]
                        self.sessions[session.session_id] = session
        except Exception as e:
            logging.error(f"Error loading sessions: {e}")
    
    def _save_data(self):
        """Сохранение сессий в файл"""
        try:
            # Конвертация в JSON-serializable формат
            sessions_data = []
            for session in self.sessions.values():
                session_dict = asdict(session)
                sessions_data.append(session_dict)
            
            data = {
                "sessions": sessions_data,
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving sessions: {e}")
    
    def get_or_create_session(self, chat_id: int, user_id: int, user_name: str) -> ChatSession:
        """Получение или создание сессии"""
        session_id = f"chat_{chat_id}_{user_id}"
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                started_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                messages=[],
                preferred_model="ollama",
                total_tokens=0
            )
        
        return self.sessions[session_id]
    
    def add_message(self, session: ChatSession, role: str, content: str, model_used: str = "unknown"):
        """Добавление сообщения в сессию"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            model_used=model_used
        )
        
        session.messages.append(message)
        session.last_activity = datetime.now().isoformat()
        session.total_tokens += len(content.split())  # Примерная оценка
        
        # Ограничение истории
        if len(session.messages) > 100:
            session.messages = session.messages[-50:]
        
        self._save_data()

class OllamaAPIBot:
    """Telegram бот с интеграцией FastAPI"""
    
    def __init__(self, bot_token: str, api_base_url: str = "http://localhost:8000"):
        self.bot_token = bot_token
        self.bot_url = f"https://api.telegram.org/bot{bot_token}"
        self.api_base_url = api_base_url
        self.api_client = None
        self.running = False
        
        # Менеджеры
        self.memory = MemoryManager()
        self.logger = logging.getLogger(__name__)
        
        # Обработка сигналов
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown"):
        """Отправка сообщения в Telegram"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
                async with session.post(f"{self.bot_url}/sendMessage", json=payload) as response:
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return None
    
    async def get_updates(self, offset: int = 0):
        """Получение обновлений от Telegram"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"offset": offset, "timeout": 10}
                async with session.get(f"{self.bot_url}/getUpdates", params=params) as response:
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to get updates: {e}")
            return None
    
    async def chat_with_ai(self, session: ChatSession, user_message: str) -> str:
        """Общение с AI через различные API"""
        
        # Подготовка контекста
        messages = []
        for msg in session.messages[-10:]:  # Последние 10 сообщений
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        # Пробуем Ollama
        model_manager = ModelManager(self.api_client)
        response = await model_manager.chat_with_ollama(messages)
        
        if response:
            return response
        
        # Fallback через FastAPI
        return await model_manager.chat_with_api_fallback(user_message, session.session_id)
    
    async def handle_message(self, update):
        """Обработка входящего сообщения"""
        try:
            message = update.get("message")
            if not message:
                return
            
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            user_name = message["from"].get("first_name", "User")
            text = message.get("text", "")
            
            if not text:
                return
            
            # Получение сессии
            session = self.memory.get_or_create_session(chat_id, user_id, user_name)
            
            # Обработка команд
            if text.startswith("/"):
                await self.handle_command(chat_id, text, session)
                return
            
            # Сохранение сообщения пользователя
            self.memory.add_message(session, "user", text)
            
            # Получение ответа от AI
            ai_response = await self.chat_with_ai(session, text)
            
            # Сохранение ответа AI
            self.memory.add_message(session, "assistant", ai_response, "ollama_api")
            
            # Отправка ответа
            await self.send_message(chat_id, ai_response)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            if "chat_id" in locals():
                await self.send_message(chat_id, "❌ Произошла ошибка при обработке сообщения")
    
    async def handle_command(self, chat_id: int, command: str, session: ChatSession):
        """Обработка команд бота"""
        
        if command == "/start":
            response = f"""🤖 **Ollama API Bot**

Привет, {session.user_name}! Я бот с интеграцией FastAPI.

**Команды:**
/status - статус системы через API
/metrics - метрики системы  
/health - проверка здоровья API
/help - эта справка

Просто пишите мне, и я отвечу через Ollama или API fallback!"""
            
        elif command == "/status":
            file_manager = FileManager(self.api_client)
            response = await file_manager.get_system_status()
            
        elif command == "/metrics":
            try:
                metrics = await self.api_client.get_metrics()
                response = f"""📊 **Метрики системы**

**Сессия**: {metrics['session_summary'].get('session_id', 'N/A')}
**Токены**: {metrics['session_summary'].get('total_tokens', 0)}
**События**: {len(metrics['session_summary'].get('events', []))}

💬 **Чат**: {len(session.messages)} сообщений, {session.total_tokens} токенов"""
            except Exception as e:
                response = f"❌ Ошибка получения метрик: {e}"
        
        elif command == "/health":
            try:
                health = await self.api_client.health_check()
                status_emoji = "🟢" if health["status"] == "healthy" else "🔴"
                response = f"""{status_emoji} **API Health Check**

**Статус**: {health['status']}
**Версия**: {health['api_version']}
**Метрики**: {'включены' if health['metrics_enabled'] else 'отключены'}
**Время**: {health['timestamp']}"""
            except Exception as e:
                response = f"❌ API недоступен: {e}"
        
        elif command == "/help":
            response = """🤖 **Ollama API Bot - Справка**

**Основные команды:**
/start - приветствие и информация
/status - статус системы LLMStruct
/metrics - метрики и статистика
/health - проверка API
/help - эта справка

**Особенности:**
✅ Интеграция с FastAPI
✅ Ollama + API fallback
✅ Отслеживание метрик
✅ Память разговоров

Просто пишите сообщения - я отвечу!"""
        
        else:
            response = "❓ Неизвестная команда. Используйте /help для справки."
        
        await self.send_message(chat_id, response)
        self.memory.add_message(session, "assistant", response, "command")
    
    async def run(self):
        """Запуск бота"""
        self.running = True
        offset = 0
        
        # Инициализация API клиента
        self.api_client = APIClient(self.api_base_url)
        
        async with self.api_client:
            self.logger.info("🚀 Ollama API Bot запущен!")
            
            # Проверка API
            try:
                health = await self.api_client.health_check()
                self.logger.info(f"✅ API доступен: {health['status']}")
            except Exception as e:
                self.logger.warning(f"⚠️ API недоступен: {e}")
            
            while self.running:
                try:
                    updates = await self.get_updates(offset)
                    
                    if updates and updates.get("ok"):
                        for update in updates.get("result", []):
                            await self.handle_message(update)
                            offset = update["update_id"] + 1
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(5)
        
        self.logger.info("✅ Bot shutdown complete")

async def main():
    """Главная функция"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return 1
    
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    bot = OllamaAPIBot(token, api_url)
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user")
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 