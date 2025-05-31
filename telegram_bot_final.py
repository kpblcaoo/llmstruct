#!/usr/bin/env python3
"""
🎯 ФИНАЛЬНАЯ версия Telegram бота для LLMStruct
- Интеграция с FastAPI ✅
- Обработка SSL ошибок ✅  
- Автовосстановление ✅
- Полное логирование ✅
"""

import os
import json
import time
import logging
import aiohttp
import asyncio
from datetime import datetime
from pathlib import Path

# Настройка логирования
log_file = Path("logs/telegram_bot_final.log")
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update, BotCommand
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram.error import NetworkError, TimedOut, RetryAfter
except ImportError:
    print("❌ Missing telegram dependencies. Install with: pip install python-telegram-bot")
    exit(1)

class FinalLLMStructBot:
    def __init__(self, token: str, api_base_url: str = "http://localhost:8000"):
        self.token = token
        self.api_base_url = api_base_url
        self.session = None
        self.max_retries = 3
        self.retry_delay = 5
        
        # Создаем приложение с расширенными настройками
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        logger.info("🎯 Final LLMStruct Bot initialized")
    
    async def get_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def api_call(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Устойчивый вызов API с повторами"""
        session = await self.get_session()
        url = f"{self.api_base_url}/api/v1{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.debug(f"✅ API {method} {endpoint} - OK")
                            return result
                        else:
                            logger.warning(f"⚠️ API {method} {endpoint} - {response.status}")
                            
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.debug(f"✅ API {method} {endpoint} - OK")
                            return result
                        else:
                            logger.warning(f"⚠️ API {method} {endpoint} - {response.status}")
                            
            except Exception as e:
                logger.warning(f"🔄 API attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    
        logger.error(f"❌ API call failed after {self.max_retries} attempts: {endpoint}")
        return {"error": f"API unavailable after {self.max_retries} attempts"}
    
    async def save_user_message(self, user_id: int, username: str, message: str) -> bool:
        """Сохранение сообщения пользователя"""
        result = await self.api_call("/memory/save", "POST", {
            "user_id": user_id,
            "username": username or "unknown",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        success = "error" not in result
        if success:
            logger.info(f"💾 Message saved: {username} - {message[:30]}...")
        return success
    
    async def get_user_history(self, user_id: int, limit: int = 5) -> list:
        """Получение истории пользователя"""
        result = await self.api_call(f"/memory/history/{user_id}?limit={limit}")
        
        if "error" not in result:
            messages = result.get("messages", [])
            logger.info(f"📖 Retrieved {len(messages)} messages")
            return messages
        return []
    
    async def chat_with_ollama(self, message: str) -> str:
        """Чат с Ollama"""
        result = await self.api_call("/chat/ollama", "POST", {
            "message": message,
            "model": "mistral:latest"
        })
        
        if "error" not in result:
            response = result.get("response", "No response")
            tokens = result.get("tokens_used", 0)
            logger.info(f"🤖 Ollama: {tokens} tokens")
            return response
        else:
            error_msg = "❌ Ollama временно недоступен"
            logger.error(f"Ollama error: {result.get('error')}")
            return error_msg
    
    async def get_system_status(self) -> dict:
        """Получение статуса системы"""
        return await self.api_call("/system/health")
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("memory", self.memory_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчики ошибок
        self.application.add_error_handler(self.error_handler)
        
        logger.info("✅ Handlers configured")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username, "/start")
        
        welcome = f"""🎯 **LLMStruct Bot Final**

Привет, {user.first_name}!

🤖 Интегрирован с FastAPI сервером
📊 Память и метрики работают  
🧠 Ollama доступна для чата

**Команды:**
• `/status` - статус системы
• `/memory` - твоя история
• `/help` - помощь

Просто напиши сообщение для чата с ИИ!"""
        
        try:
            await update.message.reply_text(welcome)
            logger.info(f"👋 Start: {user.username} ({user.id})")
        except Exception as e:
            logger.error(f"❌ Failed to send start message: {e}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username, "/status")
        
        status = await self.get_system_status()
        
        if "error" not in status:
            response = f"""✅ **System Status**

🔧 API: {status.get('status', 'unknown')}
📦 Version: {status.get('api_version', 'unknown')}  
📊 Metrics: {'✅' if status.get('metrics_enabled') else '❌'}
🤖 Ollama: {'✅' if status.get('ollama_available') else '❌'}
⏰ Time: {status.get('timestamp', 'unknown')}"""
        else:
            response = f"❌ **API Error**: {status.get('error')}"
        
        try:
            await update.message.reply_text(response)
            logger.info(f"📊 Status: {user.username}")
        except Exception as e:
            logger.error(f"❌ Failed to send status: {e}")
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /memory"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username, "/memory")
        
        history = await self.get_user_history(user.id, 5)
        
        if history:
            response = "📚 **Твоя история:**\n\n"
            for i, msg in enumerate(history[-5:], 1):
                timestamp = msg.get('timestamp', 'unknown')[:16]
                message = msg.get('message', 'no message')[:40] + "..."
                response += f"{i}. `{timestamp}` {message}\n"
        else:
            response = "📭 История пуста или недоступна"
        
        try:
            await update.message.reply_text(response)
            logger.info(f"🧠 Memory: {user.username}")
        except Exception as e:
            logger.error(f"❌ Failed to send memory: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """🎯 **LLMStruct Bot Help**

**Команды:**
• `/start` - приветствие
• `/status` - статус системы
• `/memory` - твоя история
• `/help` - эта справка

**Чат:**
Просто напиши любое сообщение для общения с ИИ!

**Логи:** `logs/telegram_bot_final.log`"""
        
        try:
            await update.message.reply_text(help_text)
            logger.info(f"❓ Help: {update.effective_user.username}")
        except Exception as e:
            logger.error(f"❌ Failed to send help: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        user = update.effective_user
        message = update.message.text
        
        logger.info(f"💬 Message from {user.username}: {message[:50]}...")
        
        # Сохраняем сообщение
        await self.save_user_message(user.id, user.username, message)
        
        try:
            # Показываем что думаем
            thinking_msg = await update.message.reply_text("🤔 Думаю...")
            
            # Получаем ответ от Ollama
            response = await self.chat_with_ollama(message)
            
            # Обновляем сообщение с ответом
            await thinking_msg.edit_text(f"🤖 {response}")
            
            logger.info(f"✅ Response sent to {user.username}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle message: {e}")
            try:
                await update.message.reply_text("❌ Произошла ошибка, попробуйте позже")
            except:
                pass
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"🚨 Bot error: {context.error}")
        
        # Попытаемся переподключиться при сетевых ошибках
        if isinstance(context.error, (NetworkError, TimedOut)):
            logger.info("🔄 Network error, will retry...")
            await asyncio.sleep(5)
        elif isinstance(context.error, RetryAfter):
            logger.info(f"🕐 Rate limited, waiting {context.error.retry_after}s...")
            await asyncio.sleep(context.error.retry_after)
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.session:
            await self.session.close()
            logger.info("🧹 Session closed")

def main():
    """Главная функция"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return 1
    
    bot = FinalLLMStructBot(token)
    
    # Команды бота
    commands = [
        BotCommand("start", "Приветствие и информация"),
        BotCommand("status", "Статус API сервера"),
        BotCommand("memory", "История сообщений"),
        BotCommand("help", "Справка по командам"),
    ]
    
    logger.info("🚀 Starting Final LLMStruct Bot...")
    
    try:
        # Устойчивый запуск
        bot.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    finally:
        logger.info("✅ Bot shutdown complete")
        return 0

if __name__ == "__main__":
    exit(main()) 