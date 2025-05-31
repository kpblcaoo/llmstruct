#!/usr/bin/env python3
"""
LLMStruct Ollama Chat Bot
Продвинутый бот с Олламой, fallback на Грок/Антропик, памятью и доступом к файлам
"""

import asyncio
import httpx
import json
import subprocess
import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ollama_chat_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

class ModelManager:
    """Управляет различными LLM провайдерами"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.default_ollama_model = "llama3.2:3b"
        
    async def chat_with_ollama(self, messages: List[Dict], model: str = None) -> Optional[str]:
        """Общение с Ollama"""
        try:
            model = model or self.default_ollama_model
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return None
    
    async def chat_with_grok(self, messages: List[Dict]) -> Optional[str]:
        """Fallback на Grok"""
        if not self.grok_api_key:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.grok_api_key}"},
                    json={
                        "model": "grok-beta",
                        "messages": messages
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Grok error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Grok request failed: {e}")
            return None
    
    async def chat_with_anthropic(self, messages: List[Dict]) -> Optional[str]:
        """Fallback на Anthropic"""
        if not self.anthropic_api_key:
            return None
            
        try:
            # Конвертируем messages для Anthropic API
            system_msg = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg += msg["content"] + "\n"
                else:
                    user_messages.append(msg)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1000,
                        "system": system_msg if system_msg else "You are a helpful assistant.",
                        "messages": user_messages
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"]
                else:
                    logger.error(f"Anthropic error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            return None

class FileManager:
    """Управляет доступом к файлам проекта через CLI"""
    
    def __init__(self):
        self.project_root = Path("/home/sma/projects/llmstruct/llmstruct")
        
    async def read_file(self, file_path: str, max_lines: int = 100) -> str:
        """Читает файл проекта безопасно"""
        try:
            full_path = self.project_root / file_path
            
            # Проверка безопасности
            if not str(full_path).startswith(str(self.project_root)):
                return "❌ Access denied: path outside project"
            
            if not full_path.exists():
                return f"❌ File not found: {file_path}"
            
            if full_path.is_dir():
                return f"❌ Path is directory: {file_path}"
            
            # Читаем файл
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if len(lines) > max_lines:
                content = ''.join(lines[:max_lines])
                content += f"\n... (truncated, {len(lines)} total lines)"
            else:
                content = ''.join(lines)
                
            return f"📄 **{file_path}**\n```\n{content}\n```"
            
        except Exception as e:
            return f"❌ Error reading {file_path}: {str(e)}"
    
    async def list_directory(self, dir_path: str = ".") -> str:
        """Показывает содержимое директории"""
        try:
            full_path = self.project_root / dir_path
            
            if not str(full_path).startswith(str(self.project_root)):
                return "❌ Access denied: path outside project"
            
            if not full_path.exists():
                return f"❌ Directory not found: {dir_path}"
            
            if not full_path.is_dir():
                return f"❌ Path is not directory: {dir_path}"
            
            items = []
            for item in sorted(full_path.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")
            
            if not items:
                return f"📁 **{dir_path}** (empty)"
            
            content = "\n".join(items[:50])  # Limit output
            if len(items) > 50:
                content += f"\n... (and {len(items)-50} more items)"
                
            return f"📁 **{dir_path}**\n```\n{content}\n```"
            
        except Exception as e:
            return f"❌ Error listing {dir_path}: {str(e)}"
    
    async def run_cli_command(self, command: str) -> str:
        """Выполняет CLI команды проекта"""
        try:
            # Безопасные CLI команды
            safe_commands = {
                "status": ["python", "-m", "llmstruct.cli", "parse", "--help"],
                "query": ["python", "-m", "llmstruct.cli", "query", "--help"],
                "context": ["python", "-m", "llmstruct.cli", "context", "--help"],
                "metrics": ["python", "-m", "llmstruct.cli", "metrics", "status"],
                "ai_status": ["python", "-c", "from auto_init_ai_system import get_ai_status; print(get_ai_status())"],
                "workflow": ["python", "-c", "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"],
                "search": ["python", "-c", "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('{}'))"],
            }
            
            # Парсим команду
            parts = command.split(' ', 1)
            cmd_name = parts[0]
            cmd_args = parts[1] if len(parts) > 1 else ""
            
            if cmd_name not in safe_commands:
                return f"❌ Command '{cmd_name}' not allowed.\nAvailable: {', '.join(safe_commands.keys())}"
            
            # Формируем команду
            cmd = safe_commands[cmd_name]
            if cmd_name == "search" and cmd_args:
                cmd = ["python", "-c", f"from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('{cmd_args}'))"]
            
            # Выполняем в рабочей директории проекта
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return f"✅ **{command}**\n```\n{result.stdout}\n```"
            else:
                return f"❌ **{command}** (exit {result.returncode})\n```\n{result.stderr}\n```"
                
        except subprocess.TimeoutExpired:
            return f"⏰ Command '{command}' timed out"
        except Exception as e:
            return f"❌ Error executing '{command}': {str(e)}"

class MemoryManager:
    """Управляет памятью и контекстом разговоров"""
    
    def __init__(self, storage_dir: str = "data/ollama_chat"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions_file = self.storage_dir / "sessions.json"
        self.global_context_file = self.storage_dir / "global_context.json"
        
        self.sessions: Dict[str, ChatSession] = {}
        self.global_context: Dict[str, Any] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Загружает данные из файлов"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.values():
                        session = ChatSession(
                            session_id=session_data["session_id"],
                            chat_id=session_data["chat_id"],
                            user_id=session_data["user_id"],
                            user_name=session_data["user_name"],
                            started_at=session_data["started_at"],
                            last_activity=session_data["last_activity"],
                            messages=[
                                ChatMessage(**msg) for msg in session_data["messages"]
                            ],
                            preferred_model=session_data.get("preferred_model", "ollama"),
                            total_tokens=session_data.get("total_tokens", 0)
                        )
                        self.sessions[session.session_id] = session
            
            if self.global_context_file.exists():
                with open(self.global_context_file, 'r', encoding='utf-8') as f:
                    self.global_context = json.load(f)
                    
            logger.info(f"📚 Loaded {len(self.sessions)} chat sessions")
            
        except Exception as e:
            logger.error(f"Failed to load memory data: {e}")
    
    def _save_data(self):
        """Сохраняет данные"""
        try:
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = {
                    "session_id": session.session_id,
                    "chat_id": session.chat_id,
                    "user_id": session.user_id,
                    "user_name": session.user_name,
                    "started_at": session.started_at,
                    "last_activity": session.last_activity,
                    "messages": [asdict(msg) for msg in session.messages],
                    "preferred_model": session.preferred_model,
                    "total_tokens": session.total_tokens
                }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            
            with open(self.global_context_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_context, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save memory data: {e}")
    
    def get_or_create_session(self, chat_id: int, user_id: int, user_name: str) -> ChatSession:
        """Получает или создает сессию"""
        session_id = f"ollama_{chat_id}_{user_id}"
        
        if session_id not in self.sessions:
            now = datetime.now().isoformat()
            session = ChatSession(
                session_id=session_id,
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                started_at=now,
                last_activity=now,
                messages=[]
            )
            self.sessions[session_id] = session
            
        return self.sessions[session_id]
    
    def add_message(self, session: ChatSession, role: str, content: str, model_used: str = "unknown"):
        """Добавляет сообщение в сессию"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            model_used=model_used
        )
        
        session.messages.append(message)
        session.last_activity = message.timestamp
        
        # Ограничиваем количество сообщений
        if len(session.messages) > 50:
            session.messages = session.messages[-40:]  # Оставляем последние 40
        
        # Автосохранение
        if len(session.messages) % 5 == 0:
            self._save_data()
    
    def get_conversation_context(self, session: ChatSession, max_messages: int = 10) -> List[Dict[str, str]]:
        """Получает контекст разговора для LLM"""
        recent_messages = session.messages[-max_messages:] if session.messages else []
        
        context = []
        for msg in recent_messages:
            if msg.role in ["user", "assistant"]:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return context

class OllamaChatBot:
    """Основной класс Telegram бота"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.last_update_id = 0
        
        # Инициализация компонентов
        self.model_manager = ModelManager()
        self.file_manager = FileManager()
        self.memory_manager = MemoryManager()
        
        logger.info("🤖 OllamaChatBot initialized")
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown"):
        """Отправляет сообщение в Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        # Разбиваем длинные сообщения
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for i, part in enumerate(parts):
                await self._send_single_message(chat_id, f"**Part {i+1}/{len(parts)}:**\n{part}", parse_mode)
        else:
            await self._send_single_message(chat_id, text, parse_mode)
    
    async def _send_single_message(self, chat_id: int, text: str, parse_mode: str):
        """Отправляет одно сообщение"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data)
                return response.json()
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                return None
    
    async def get_updates(self):
        """Получает обновления от Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 10
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params)
                return response.json()
            except Exception as e:
                logger.error(f"Failed to get updates: {e}")
                return {"ok": False, "result": []}
    
    async def send_task_report(self, task_description: str, status: str, details: str = ""):
        """Отправляет отчет о выполнении задачи в чат разработчика"""
        # Здесь можно указать chat_id разработчика
        developer_chat_id = -4938821563  # Ваш chat_id
        
        report = f"""📋 **Task Report**
        
**Task:** {task_description}
**Status:** {status}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{details}
"""
        
        await self.send_message(developer_chat_id, report)
        logger.info(f"📋 Task report sent: {task_description} - {status}")
    
    async def chat_with_ai(self, session: ChatSession, user_message: str) -> str:
        """Общается с AI (Ollama + fallback)"""
        context = self.memory_manager.get_conversation_context(session)
        
        # Добавляем текущее сообщение пользователя
        context.append({"role": "user", "content": user_message})
        
        # Пробуем Ollama
        logger.info(f"🦙 Trying Ollama for user {session.user_name}")
        response = await self.model_manager.chat_with_ollama(context)
        
        if response:
            self.memory_manager.add_message(session, "assistant", response, "ollama")
            return f"🦙 **Ollama:** {response}"
        
        # Fallback на Grok
        logger.info("🚀 Ollama failed, trying Grok")
        response = await self.model_manager.chat_with_grok(context)
        
        if response:
            self.memory_manager.add_message(session, "assistant", response, "grok")
            return f"🚀 **Grok:** {response}"
        
        # Fallback на Anthropic
        logger.info("🤖 Grok failed, trying Anthropic")
        response = await self.model_manager.chat_with_anthropic(context)
        
        if response:
            self.memory_manager.add_message(session, "assistant", response, "anthropic")
            return f"🤖 **Claude:** {response}"
        
        # Все провайдеры недоступны
        return "❌ **All AI providers are currently unavailable**\nPlease try again later."
    
    async def handle_message(self, update):
        """Обрабатывает входящее сообщение"""
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_id = message.get("from", {}).get("id")
        user_name = message.get("from", {}).get("first_name", "User")
        
        if not chat_id or not text or not user_id:
            return
        
        # Получаем сессию
        session = self.memory_manager.get_or_create_session(chat_id, user_id, user_name)
        
        # Добавляем пользовательское сообщение в память
        self.memory_manager.add_message(session, "user", text)
        
        logger.info(f"💬 Message from {user_name}: {text[:50]}...")
        
        # Обрабатываем команды
        if text.startswith("/start"):
            welcome = """🤖 **LLMStruct Ollama Chat Bot**

**Features:**
• 🦙 Chat with Ollama (primary)
• 🚀 Fallback to Grok API
• 🤖 Fallback to Claude
• 📚 Memory & context preservation
• 📁 Project file access
• ⚙️ CLI command execution

**Commands:**
• `/file <path>` - Read project file
• `/ls <path>` - List directory
• `/cli <command>` - Run CLI command
• `/memory` - Session statistics
• `/models` - Switch AI model
• `/help` - Show this help

Ready to help! 🚀"""
            
            await self.send_message(chat_id, welcome)
            
        elif text.startswith("/file "):
            file_path = text[6:].strip()
            result = await self.file_manager.read_file(file_path)
            await self.send_message(chat_id, result)
            
        elif text.startswith("/ls"):
            dir_path = text[3:].strip() or "."
            result = await self.file_manager.list_directory(dir_path)
            await self.send_message(chat_id, result)
            
        elif text.startswith("/cli "):
            command = text[5:].strip()
            await self.send_message(chat_id, f"⚙️ Running: `{command}`")
            result = await self.file_manager.run_cli_command(command)
            await self.send_message(chat_id, result)
            
        elif text.startswith("/memory"):
            stats = f"""🧠 **Memory Statistics**

**Session:** {session.session_id}
• Messages: {len(session.messages)}
• Started: {session.started_at[:19]}
• Last activity: {session.last_activity[:19]}
• Preferred model: {session.preferred_model}

**Global:**
• Total sessions: {len(self.memory_manager.sessions)}"""
            
            await self.send_message(chat_id, stats)
            
        elif text.startswith("/models"):
            models_info = """🤖 **Available AI Models**

**Primary:** 🦙 Ollama (llama3.2:3b)
**Fallback:** 🚀 Grok Beta
**Fallback:** 🤖 Claude Haiku

Models are tried in order until one succeeds.
Ollama must be running locally on port 11434."""
            
            await self.send_message(chat_id, models_info)
            
        elif text.startswith("/help"):
            help_text = """🆘 **Help & Commands**

**File Access:**
• `/file src/llmstruct/cli.py` - Read file
• `/ls src/llmstruct` - List directory contents
• `/ls` - List root directory

**CLI Commands:**
• `/cli status` - Project status
• `/cli metrics` - Show metrics
• `/cli ai_status` - AI system status
• `/cli workflow` - Workflow status
• `/cli search context` - Search capabilities

**Other:**
• `/memory` - Memory statistics
• `/models` - Available AI models
• Regular messages go to AI chat

Everything is logged and context-aware! 📚"""
            
            await self.send_message(chat_id, help_text)
            
        else:
            # Обычное сообщение - отправляем в AI
            await self.send_message(chat_id, "🤔 *Thinking...*")
            response = await self.chat_with_ai(session, text)
            await self.send_message(chat_id, response)
    
    async def run(self):
        """Основной цикл бота"""
        logger.info("🚀 LLMStruct Ollama Chat Bot starting...")
        
        while True:
            try:
                updates = await self.get_updates()
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        self.last_update_id = update["update_id"]
                        await self.handle_message(update)
                
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopping...")
                self.memory_manager._save_data()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

async def main():
    """Точка входа"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        return
    
    # Создаем директории
    Path("logs").mkdir(exist_ok=True)
    Path("data/ollama_chat").mkdir(parents=True, exist_ok=True)
    
    # Запускаем бота
    bot = OllamaChatBot(bot_token)
    
    # Отправляем стартовый отчет
    await bot.send_task_report(
        "Ollama Chat Bot Startup",
        "✅ Success", 
        "Bot initialized with Ollama + Grok/Anthropic fallback, memory system, and file access"
    )
    
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 