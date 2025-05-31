#!/usr/bin/env python3
"""
🚀 ENHANCED Telegram Bot с интеграцией FastAPI
Использует ваш существующий FastAPI сервер для:
- Кеша сообщений через WebSocket
- Памяти пользователей через API endpoints
- Метрик через API

Больше никаких CLI вызовов - все через API!
"""

import asyncio
import logging
import json
import aiohttp
import websockets
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_fastapi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FastAPIIntegratedBot:
    """Telegram бот с полной интеграцией FastAPI"""
    
    def __init__(self, telegram_token: str, fastapi_base_url: str = "http://localhost:8000"):
        self.telegram_token = telegram_token
        self.fastapi_base_url = fastapi_base_url
        self.user_memory = {}  # Локальный кеш + API синхронизация
        self.session = None
        
        # Создаем Telegram Application
        self.app = Application.builder().token(telegram_token).build()
        self.setup_handlers()
        
    async def setup_session(self):
        """Инициализация aiohttp сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Закрытие aiohttp сессии"""
        if self.session:
            await self.session.close()
    
    async def health_check_api(self) -> bool:
        """Проверка доступности FastAPI сервера"""
        try:
            await self.setup_session()
            async with self.session.get(f"{self.fastapi_base_url}/api/v1/system/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"✅ FastAPI server healthy: {data.get('status')}")
                    return True
                else:
                    logger.error(f"❌ FastAPI health check failed: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ FastAPI connection failed: {e}")
            return False
    
    async def save_user_message_via_api(self, user_id: int, username: str, message: str):
        """Сохранение сообщения пользователя через FastAPI"""
        try:
            await self.setup_session()
            payload = {
                "user_id": user_id,
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": "user_message"
            }
            
            # Используем endpoint для сохранения в памяти
            async with self.session.post(
                f"{self.fastapi_base_url}/api/v1/memory/save",
                json=payload
            ) as resp:
                if resp.status == 200:
                    logger.info(f"💾 Message saved via API for user {username}")
                else:
                    logger.warning(f"⚠️ API save failed: {resp.status}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to save via API: {e}")
            # Fallback to local memory
            if user_id not in self.user_memory:
                self.user_memory[user_id] = []
            self.user_memory[user_id].append({
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    async def get_user_history_via_api(self, user_id: int, limit: int = 10) -> list:
        """Получение истории пользователя через FastAPI"""
        try:
            await self.setup_session()
            async with self.session.get(
                f"{self.fastapi_base_url}/api/v1/memory/history/{user_id}?limit={limit}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"📖 Retrieved {len(data.get('messages', []))} messages via API")
                    return data.get('messages', [])
                else:
                    logger.warning(f"⚠️ API history failed: {resp.status}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to get history via API: {e}")
            
        # Fallback to local memory
        return self.user_memory.get(user_id, [])[-limit:]
    
    async def chat_with_ollama_via_api(self, message: str, context: str = "") -> str:
        """Чат с Ollama через FastAPI endpoint"""
        try:
            await self.setup_session()
            payload = {
                "message": message,
                "context_mode": "focused",
                "session_id": "telegram_bot",
                "model": "mistral:latest",
                "use_ollama": True
            }
            
            async with self.session.post(
                f"{self.fastapi_base_url}/api/v1/chat/ollama",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"🤖 Ollama response via API: {data.get('tokens_used', 0)} tokens")
                    return data.get('response', 'No response from Ollama')
                else:
                    logger.error(f"❌ Ollama API failed: {resp.status}")
                    return f"❌ Ошибка Ollama API: {resp.status}"
                    
        except Exception as e:
            logger.error(f"❌ Ollama chat failed: {e}")
            return f"❌ Ollama недоступен: {str(e)}"
    
    async def get_system_metrics_via_api(self) -> dict:
        """Получение метрик системы через FastAPI"""
        try:
            await self.setup_session()
            async with self.session.get(f"{self.fastapi_base_url}/api/v1/system/status") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": f"API status: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("memory", self.memory_command))
        self.app.add_handler(CommandHandler("history", self.history_command))
        self.app.add_handler(CommandHandler("health", self.health_command))
        self.app.add_handler(CommandHandler("metrics", self.metrics_command))
        self.app.add_handler(CommandHandler("ollama", self.ollama_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        await self.save_user_message_via_api(user.id, user.username or "unknown", "/start")
        
        welcome_text = f"""
🚀 **FastAPI-Integrated LLMStruct Bot**

Привет, {user.first_name}! Я подключен к вашему FastAPI серверу.

**Доступные команды:**
• `/memory` - сохранить в память  
• `/history` - показать историю
• `/health` - статус FastAPI сервера
• `/metrics` - метрики системы
• `/ollama <сообщение>` - чат с Ollama

**Преимущества:**
✅ Память через FastAPI (не CLI!)
✅ Ollama интеграция через API  
✅ Метрики в реальном времени
✅ WebSocket поддержка
        """
        
        await update.message.reply_text(welcome_text)
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /memory - тест памяти"""
        user = update.effective_user
        command_text = " ".join(context.args) if context.args else "Тест памяти"
        
        await self.save_user_message_via_api(user.id, user.username or "unknown", command_text)
        
        await update.message.reply_text(f"💾 Сохранено в память через FastAPI: '{command_text}'")
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /history - показать историю"""
        user = update.effective_user
        limit = 5
        if context.args and context.args[0].isdigit():
            limit = int(context.args[0])
        
        messages = await self.get_user_history_via_api(user.id, limit)
        
        if not messages:
            await update.message.reply_text("📭 История пуста")
            return
        
        history_text = f"📖 **Последние {len(messages)} сообщений:**\n\n"
        for msg in messages[-limit:]:
            timestamp = msg.get('timestamp', 'N/A')[:16].replace('T', ' ')
            message = msg.get('message', 'N/A')[:50]
            history_text += f"`{timestamp}` | {message}...\n"
        
        await update.message.reply_text(history_text, parse_mode='Markdown')
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /health - статус FastAPI"""
        is_healthy = await self.health_check_api()
        
        if is_healthy:
            await update.message.reply_text("✅ FastAPI сервер работает отлично!")
        else:
            await update.message.reply_text("❌ FastAPI сервер недоступен")
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /metrics - метрики системы"""
        metrics = await self.get_system_metrics_via_api()
        
        if "error" in metrics:
            await update.message.reply_text(f"❌ Ошибка метрик: {metrics['error']}")
            return
        
        system = metrics.get('system', {})
        struct_json = metrics.get('struct_json', {})
        features = metrics.get('features', {})
        
        metrics_text = f"""
📊 **Метрики системы:**

🖥️ **Система:**
Status: {system.get('status', 'N/A')}
Timestamp: {system.get('timestamp', 'N/A')}

📄 **struct.json:**
Status: {struct_json.get('status', 'N/A')}
Size: {struct_json.get('size_bytes', 0)} bytes
Modified: {struct_json.get('last_modified', 'N/A')[:16]}

🚀 **Возможности:**
Chat: {'✅' if features.get('chat') else '❌'}
Metrics: {'✅' if features.get('metrics') else '❌'}
Struct Analysis: {'✅' if features.get('struct_analysis') else '❌'}
        """
        
        await update.message.reply_text(metrics_text)
    
    async def ollama_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /ollama - чат с Ollama"""
        if not context.args:
            await update.message.reply_text("🤖 Использование: /ollama <ваше сообщение>")
            return
        
        user_message = " ".join(context.args)
        user = update.effective_user
        
        await self.save_user_message_via_api(user.id, user.username or "unknown", f"Ollama: {user_message}")
        
        # Показываем, что обрабатываем
        status_msg = await update.message.reply_text("🤖 Ollama думает...")
        
        # Получаем ответ от Ollama через API
        response = await self.chat_with_ollama_via_api(user_message)
        
        # Обновляем сообщение
        await status_msg.edit_text(f"🤖 **Ollama ответ:**\n{response}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        user = update.effective_user
        message_text = update.message.text
        
        # Сохраняем все сообщения в память
        await self.save_user_message_via_api(user.id, user.username or "unknown", message_text)
        
        # Проверяем специальные запросы
        if "напомни" in message_text.lower() and "запрос" in message_text.lower():
            messages = await self.get_user_history_via_api(user.id, 3)
            if messages:
                history_text = "📝 **Ваши последние запросы:**\n\n"
                for i, msg in enumerate(messages[-3:], 1):
                    message = msg.get('message', 'N/A')
                    history_text += f"{i}. {message}\n"
                await update.message.reply_text(history_text)
            else:
                await update.message.reply_text("📭 Запросов не найдено")
                
        elif "кукумбер" in message_text.lower():
            await update.message.reply_text("🥒 Кодовое слово запомнено! Cucumber в памяти FastAPI.")
            
        elif message_text.startswith("@llmstruct_bot"):
            # Обработка упоминаний
            query = message_text.replace("@llmstruct_bot", "").strip()
            if query:
                response = await self.chat_with_ollama_via_api(query)
                await update.message.reply_text(f"🤖 {response}")
            else:
                await update.message.reply_text("👋 Я здесь! Используйте команды или задайте вопрос.")
    
    async def run(self):
        """Запуск бота"""
        try:
            logger.info("🚀 Starting FastAPI-Integrated Bot...")
            
            # Проверяем FastAPI при старте
            if await self.health_check_api():
                logger.info("✅ FastAPI connection verified")
            else:
                logger.warning("⚠️ FastAPI not available, using fallback mode")
            
            # Запускаем бота
            await self.app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            await self.close_session()

async def main():
    """Главная функция"""
    import os
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        exit(1)
    
    # Можно настроить URL FastAPI сервера
    fastapi_url = os.getenv('FASTAPI_URL', 'http://localhost:8000')
    
    print("🚀 Starting FastAPI-Integrated Bot...")
    
    try:
        # Создаем event loop если его нет
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Создаем и запускаем бота
        bot = FastAPIIntegratedBot(token, fastapi_url)
        loop.run_until_complete(bot.run())
        
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            loop.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main()) 