#!/usr/bin/env python3
"""
🧪 Тестовый Telegram бот для проверки интеграции с FastAPI
Простая версия для форграунд тестирования
"""

import os
import json
import time
import logging
import aiohttp
import asyncio
from datetime import datetime

# Настройка логирования с выводом в файл и консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update, BotCommand
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("❌ Missing telegram dependencies. Install with: pip install python-telegram-bot")
    exit(1)

class TelegramBotTest:
    def __init__(self, token: str, api_base_url: str = "http://localhost:8000"):
        self.token = token
        self.api_base_url = api_base_url
        self.session = None
        
        # Создаем приложение
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        logger.info("🧪 Test bot initialized")
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def api_call(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Универсальный вызов API"""
        try:
            session = await self.get_session()
            url = f"{self.api_base_url}/api/v1{endpoint}"
            
            if method == "GET":
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API GET error {response.status}: {endpoint}")
                        return {"error": f"HTTP {response.status}"}
            
            elif method == "POST":
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API POST error {response.status}: {endpoint}")
                        return {"error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {"error": str(e)}
    
    async def save_user_message(self, user_id: int, username: str, message: str) -> bool:
        """Сохранение сообщения пользователя"""
        result = await self.api_call("/memory/save", "POST", {
            "user_id": user_id,
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        success = "error" not in result
        if success:
            logger.info(f"💾 Message saved for {username}: {message[:50]}...")
        else:
            logger.error(f"❌ Failed to save message: {result.get('error')}")
        return success
    
    async def get_user_history(self, user_id: int, limit: int = 5) -> list:
        """Получение истории пользователя"""
        result = await self.api_call(f"/memory/history/{user_id}?limit={limit}")
        
        if "error" not in result:
            messages = result.get("messages", [])
            logger.info(f"📖 Retrieved {len(messages)} messages for user {user_id}")
            return messages
        else:
            logger.error(f"❌ Failed to get history: {result.get('error')}")
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
            logger.info(f"🤖 Ollama response: {tokens} tokens")
            return response
        else:
            error_msg = f"❌ Ollama error: {result.get('error')}"
            logger.error(error_msg)
            return error_msg
    
    async def get_system_status(self) -> dict:
        """Получение статуса системы"""
        return await self.api_call("/system/health")
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("memory", self.memory_command))
        self.application.add_handler(CommandHandler("chat", self.chat_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("✅ Handlers setup complete")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username or "unknown", "/start")
        
        welcome = f"""🧪 **Test Bot Active**

Привет, {user.first_name}!

**Команды:**
• `/status` - статус API сервера
• `/memory` - твоя история  
• `/chat <сообщение>` - чат с Ollama
• Просто напиши сообщение для автоматического чата

**Логи:** `telegram_bot_test.log`"""
        
        await update.message.reply_text(welcome)
        logger.info(f"👋 Start command from {user.username} ({user.id})")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username or "unknown", "/status")
        
        status = await self.get_system_status()
        
        if "error" not in status:
            response = f"""✅ **System Status**

API: {status.get('status', 'unknown')}
Version: {status.get('api_version', 'unknown')}
Metrics: {'✅' if status.get('metrics_enabled') else '❌'}
Ollama: {'✅' if status.get('ollama_available') else '❌'}
Time: {status.get('timestamp', 'unknown')}"""
        else:
            response = f"❌ **API Error**: {status.get('error')}"
        
        await update.message.reply_text(response)
        logger.info(f"📊 Status command from {user.username}")
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /memory"""
        user = update.effective_user
        await self.save_user_message(user.id, user.username or "unknown", "/memory")
        
        history = await self.get_user_history(user.id, 5)
        
        if history:
            response = "📚 **Твоя история (последние 5):**\n\n"
            for msg in history[-5:]:
                timestamp = msg.get('timestamp', 'unknown')[:16]  # YYYY-MM-DD HH:MM
                message = msg.get('message', 'no message')[:50]
                response += f"• `{timestamp}` {message}\n"
        else:
            response = "📭 История пуста"
        
        await update.message.reply_text(response)
        logger.info(f"🧠 Memory command from {user.username}")
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /chat"""
        user = update.effective_user
        message_text = update.message.text
        
        # Извлекаем сообщение после команды
        if len(context.args) > 0:
            user_message = " ".join(context.args)
        else:
            await update.message.reply_text("❌ Напиши: `/chat твое сообщение`")
            return
        
        await self.save_user_message(user.id, user.username or "unknown", message_text)
        
        # Показываем что думаем
        await update.message.reply_text("🤔 Думаю...")
        
        # Получаем ответ от Ollama
        response = await self.chat_with_ollama(user_message)
        
        await update.message.reply_text(f"🤖 {response}")
        logger.info(f"💬 Chat command from {user.username}: {user_message[:30]}...")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        user = update.effective_user
        message = update.message.text
        
        await self.save_user_message(user.id, user.username or "unknown", message)
        
        # Автоматический чат с Ollama
        await update.message.reply_text("🤔 Отвечаю...")
        response = await self.chat_with_ollama(message)
        await update.message.reply_text(f"🤖 {response}")
        
        logger.info(f"💬 Message from {user.username}: {message[:30]}...")
    
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
        return
    
    bot = TelegramBotTest(token)
    
    # Команды бота
    commands = [
        BotCommand("start", "Приветствие"),
        BotCommand("status", "Статус API сервера"),
        BotCommand("memory", "История сообщений"),
        BotCommand("chat", "Чат с Ollama"),
    ]
    
    logger.info("🚀 Starting test bot...")
    
    try:
        # Запуск в polling режиме
        bot.application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        # Cleanup не работает в синхронном контексте
        logger.info("✅ Bot shutdown complete")

if __name__ == "__main__":
    main() 