#!/usr/bin/env python3
"""
Telegram Bot for LLMStruct Integration
Безопасная интеграция в tmp директории
С интеллектуальной системой памяти и кеширования
"""

import asyncio
import httpx
import json
import subprocess
import os
import logging
from typing import Optional
from memory_manager import TelegramMemoryManager

# Простая реализация без зависимостей от telegram библиотек
# Используем polling через Bot API

class LLMStructTelegramBot:
    def __init__(self, bot_token: str, api_base: str = "http://localhost:8000"):
        self.bot_token = bot_token
        self.api_base = api_base
        self.api_key = "dev-key"  # Для разработки
        self.last_update_id = 0
        self.session_id = "telegram-bot-session"
        
        # Инициализация системы памяти
        self.memory = TelegramMemoryManager()
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🧠 Memory system initialized")
        stats = self.memory.get_memory_stats()
        self.logger.info(f"📊 Memory stats: {stats['active_sessions']} sessions, {stats['total_messages']} messages, {stats['unique_users']} users")
        
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown"):
        """Отправка сообщения в Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text[:4096],  # Telegram limit
            "parse_mode": parse_mode
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data)
                return response.json()
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")
                return None
    
    async def get_updates(self):
        """Получение обновлений от Telegram"""
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
                self.logger.error(f"Failed to get updates: {e}")
                return {"ok": False, "result": []}
    
    async def execute_command(self, command: str) -> str:
        """Выполнение системной команды безопасно"""
        try:
            # Простые безопасные команды
            safe_commands = {
                "date": ["date"],
                "pwd": ["pwd"], 
                "ls": ["ls", "-la"],
                "ps": ["ps", "aux"],
                "df": ["df", "-h"],
                "free": ["free", "-h"],
                "uptime": ["uptime"],
                "whoami": ["whoami"]
            }
            
            if command in safe_commands:
                result = subprocess.run(
                    safe_commands[command], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                return f"```\n{result.stdout}\n```" if result.stdout else f"Error: {result.stderr}"
            else:
                return f"❌ Command '{command}' not allowed. Available: {', '.join(safe_commands.keys())}"
                
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"
    
    async def chat_with_llm(self, message: str, context_mode: str = "focused", session=None) -> str:
        """Отправка сообщения в LLM через наш API с учетом контекста памяти"""
        url = f"{self.api_base}/api/v1/chat/message"
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Строим контекст с учетом истории разговора
        enhanced_message = message
        if session and len(session.messages) > 1:
            # Добавляем краткий контекст предыдущих сообщений
            recent_context = []
            for msg in session.messages[-3:]:  # Последние 3 сообщения
                if msg.role == "user":
                    recent_context.append(f"👤 {msg.content}")
                elif msg.role == "assistant":
                    recent_context.append(f"🤖 {msg.content[:100]}...")
            
            if recent_context:
                enhanced_message = f"Контекст разговора:\n{chr(10).join(recent_context)}\n\nТекущий вопрос: {message}"
        
        data = {
            "content": enhanced_message,
            "context_mode": context_mode,
            "session_id": session.session_id if session else self.session_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("content", "No response from LLM")
                else:
                    return f"❌ API Error: {response.status_code}"
            except Exception as e:
                return f"❌ Failed to reach LLM API: {str(e)}"
    
    async def handle_message(self, update):
        """Обработка входящего сообщения с интеллектуальной памятью"""
        self.logger.info(f"🔍 Raw update: {update}")
        
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_id = message.get("from", {}).get("id")
        user_name = message.get("from", {}).get("first_name", "User")
        
        self.logger.info(f"📩 Parsed - chat_id: {chat_id}, text: '{text}', user: {user_name}")
        
        if not chat_id or not text or not user_id:
            self.logger.warning(f"❌ Skipping message - missing required fields")
            return
        
        # Получаем или создаем сессию пользователя
        session = self.memory.get_or_create_session(chat_id, user_id, user_name)
        self.logger.info(f"🧠 Using session: {session.session_id} (messages: {session.message_count})")
        
        # Команды
        if text.startswith("/cmd "):
            self.logger.info("🔧 Processing /cmd command")
            command = text[5:].strip()
            await self.send_message(chat_id, f"🔧 Executing: `{command}`")
            result = await self.execute_command(command)
            await self.send_message(chat_id, result)
            
            # Сохраняем в память
            self.memory.add_message(session, "user", f"/cmd {command}", user_name)
            self.memory.add_message(session, "assistant", result)
            
        elif text.startswith("/start"):
            self.logger.info("🚀 Processing /start command")
            
            # Получаем статистику пользователя
            user_stats = self.memory.get_user_stats(user_id)
            
            welcome = """🤖 **LLMStruct Telegram Bot с памятью**

**Commands:**
• `/cmd <command>` - Execute system command
• Regular message - Chat with LLM
• `/status` - Check API status
• `/memory` - Memory statistics
• `/profile` - Your profile info

**Available commands:**
`date`, `pwd`, `ls`, `ps`, `df`, `free`, `uptime`, `whoami`
"""
            
            if user_stats["profile"]:
                interests = user_stats["profile"].get("interests", [])
                if interests:
                    welcome += f"\n🎯 **Ваши интересы:** {', '.join(interests[:5])}"
                
            welcome += "\nReady to help! 🚀"
            await self.send_message(chat_id, welcome)
            
        elif text.startswith("/status"):
            self.logger.info("📊 Processing /status command")
            # Проверка статуса API
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.api_base}/api/v1/system/health")
                    if response.status_code == 200:
                        memory_stats = self.memory.get_memory_stats()
                        status_msg = f"""✅ **LLMStruct API is online!**
                        
🧠 **Memory System:**
• Active sessions: {memory_stats['active_sessions']}
• Total messages: {memory_stats['total_messages']}
• Unique users: {memory_stats['unique_users']}"""
                        await self.send_message(chat_id, status_msg)
                    else:
                        await self.send_message(chat_id, f"❌ API Error: {response.status_code}")
            except Exception as e:
                await self.send_message(chat_id, f"❌ API unreachable: {str(e)}")
                
        elif text.startswith("/memory"):
            self.logger.info("🧠 Processing /memory command")
            memory_stats = self.memory.get_memory_stats()
            user_stats = self.memory.get_user_stats(user_id)
            
            memory_info = f"""🧠 **Memory Statistics**

**Global:**
• Active sessions: {memory_stats['active_sessions']}
• Total messages: {memory_stats['total_messages']}
• Unique users: {memory_stats['unique_users']}

**Your session:**
• Messages in session: {user_stats['active_session']['message_count']}
• Started: {user_stats['active_session']['started_at'][:19] if user_stats['active_session']['started_at'] else 'Now'}
• Total messages: {user_stats['profile'].get('message_count', 0)}"""
            
            await self.send_message(chat_id, memory_info)
            
        elif text.startswith("/profile"):
            self.logger.info("👤 Processing /profile command")
            user_stats = self.memory.get_user_stats(user_id)
            profile = user_stats["profile"]
            
            if profile:
                profile_info = f"""👤 **Your Profile**

• First seen: {profile.get('first_seen', 'Unknown')[:19]}
• Total messages: {profile.get('message_count', 0)}
• Preferred language: {profile.get('preferred_language', 'Unknown')}
• Interests: {', '.join(profile.get('interests', [])) or 'None detected yet'}"""
            else:
                profile_info = "👤 No profile data yet. Start chatting to build your profile!"
                
            await self.send_message(chat_id, profile_info)
                
        else:
            # Обычное сообщение - отправляем в LLM с контекстом памяти
            self.logger.info(f"🤖 Processing regular message for LLM: '{text}'")
            self.logger.info(f"💭 Session context: {len(session.messages)} previous messages")
            
            await self.send_message(chat_id, "🤔 *Thinking...*")
            
            # Сохраняем пользовательское сообщение
            self.memory.add_message(session, "user", text, user_name)
            
            self.logger.info("💭 Sending to LLM...")
            response = await self.chat_with_llm(text, session=session)
            self.logger.info(f"✅ LLM response received: {response[:100]}...")
            
            # Сохраняем ответ ассистента
            self.memory.add_message(session, "assistant", response)
            
            # Разбиваем длинные ответы
            if len(response) > 4000:
                parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for i, part in enumerate(parts):
                    await self.send_message(chat_id, f"**Part {i+1}/{len(parts)}:**\n{part}")
            else:
                await self.send_message(chat_id, response)
    
    async def run(self):
        """Основной цикл бота"""
        self.logger.info("🤖 LLMStruct Telegram Bot starting...")
        
        # Очищаем старые сессии при запуске
        self.memory.cleanup_old_sessions()
        
        while True:
            try:
                updates = await self.get_updates()
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        self.last_update_id = update["update_id"]
                        await self.handle_message(update)
                
                await asyncio.sleep(1)  # Polling interval
                
            except KeyboardInterrupt:
                self.logger.info("Bot stopping...")
                # Сохраняем все данные перед выходом
                self.memory.save()
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

async def main():
    """Точка входа"""
    # Получаем токен из переменной окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        print("Get token from @BotFather on Telegram")
        return
    
    # Проверяем что API запущен
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/system/health")
            if response.status_code != 200:
                print("❌ LLMStruct API is not running on localhost:8000")
                print("Start it with: source venv/bin/activate && python test_api.py")
                return
    except:
        print("❌ Cannot connect to LLMStruct API")
        print("Make sure it's running on localhost:8000")
        return
    
    # Запускаем бота
    bot = LLMStructTelegramBot(bot_token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 