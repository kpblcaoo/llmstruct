#!/usr/bin/env python3
"""
LLMStruct Chat Bot - Улучшенная версия для взаимодействия с Cursor
"""

import os
import json
import time
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from telegram import Update, BotCommand
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("❌ Missing telegram dependencies. Install with: pip install python-telegram-bot")
    exit(1)

# Инициализация метрик при старте бота
try:
    import sys
    sys.path.append('.')
    from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event, track_task_start, track_task_complete
    METRICS_AVAILABLE = True
    logger.info("📊 Metrics system loaded")
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("⚠️ Metrics system not available")

class LLMStructChatBot:
    """Улучшенный чат-бот для LLMStruct с логированием для Cursor"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Настройка файлов для логирования
        self.logs_dir = Path("logs/telegram")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл для логирования сообщений (читаемый Cursor'ом)
        self.messages_log = self.logs_dir / "user_messages.log"
        self.cursor_commands = self.logs_dir / "cursor_commands.log"
        
        self.setup_handlers()
        
        if METRICS_AVAILABLE:
            track_workflow_event("chat_bot_startup")
    
    def log_user_message(self, user_info: dict, message: str, message_type: str = "text"):
        """Логирует сообщения пользователя в читаемый файл для Cursor"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""
=== {timestamp} ===
👤 USER: {user_info.get('first_name', 'Unknown')} (@{user_info.get('username', 'unknown')})
📱 TYPE: {message_type}
💬 MESSAGE: {message}
{'='*60}
"""
        
        with open(self.messages_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Если это команда для Cursor, дублируем в отдельный файл
        if any(keyword in message.lower() for keyword in ['cursor', 'claude', 'продолжи', 'continue', 'исправь', 'fix']):
            with open(self.cursor_commands, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} | CURSOR COMMAND: {message}\n")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("metrics", self.metrics_command))
        self.application.add_handler(CommandHandler("dev", self.dev_command))
        self.application.add_handler(CommandHandler("cursor", self.cursor_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "start")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/start", "command")
        
        user_name = update.effective_user.first_name
        welcome_message = f"""👋 Привет, {user_name}!

🧠 Я **LLMStruct Chat Bot** - улучшенная версия для работы с Cursor!

**🎯 Новые возможности:**
• 📝 Логирую все сообщения для Cursor'а
• 🤖 Взаимодействие с AI ассистентом
• 📊 Полная интеграция с метриками
• 🔧 Режим разработчика

**📋 Команды:**
/help - все команды
/status - статус системы
/metrics - метрики проекта
/cursor - взаимодействие с Cursor
/logs - показать последние сообщения
/dev - режим разработчика

**💬 Два режима работы:**
1. **Обычный диалог** - просто пиши сообщения
2. **Команды для Cursor** - используй ключевые слова: "cursor", "claude", "продолжи", "исправь"

Все твои сообщения логируются в `logs/telegram/user_messages.log` 📄
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def cursor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /cursor - информация о взаимодействии с Cursor"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "cursor")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/cursor", "command")
        
        cursor_text = """🤖 **Взаимодействие с Cursor/Claude**

**📝 Логирование:**
• Все сообщения → `logs/telegram/user_messages.log`
• Команды для Cursor → `logs/telegram/cursor_commands.log`

**🎯 Ключевые слова для Cursor:**
• "cursor" - прямое обращение
• "claude" - обращение к AI
• "продолжи" / "continue" - продолжить работу
• "исправь" / "fix" - исправить проблему

**💡 Примеры команд:**
"Cursor, покажи статус метрик"
"Claude, исправь бота"
"Продолжи работу над API"

**📊 Статус логирования:**
• Файл сообщений: ✅ Активен
• Команды Cursor: ✅ Отслеживаются
• Интеграция метрик: """ + ("✅ Включена" if METRICS_AVAILABLE else "❌ Отключена") + """

Cursor может читать эти логи и отвечать на твои команды! 🚀
"""
        
        await update.message.reply_text(cursor_text, parse_mode='Markdown')
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /logs - показать последние сообщения"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "logs")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/logs", "command")
        
        try:
            # Читаем последние 5 сообщений
            if self.messages_log.exists():
                with open(self.messages_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Берем последние записи
                entries = content.split('===')[-6:-1]  # Последние 5 записей
                
                logs_text = "📄 **Последние сообщения:**\n\n"
                for entry in entries:
                    if entry.strip():
                        lines = entry.strip().split('\n')
                        if len(lines) >= 3:
                            timestamp = lines[0]
                            message_line = next((line for line in lines if line.startswith('💬 MESSAGE:')), '')
                            if message_line:
                                message = message_line.replace('💬 MESSAGE:', '').strip()
                                logs_text += f"`{timestamp}` {message[:50]}{'...' if len(message) > 50 else ''}\n"
                
                logs_text += f"\n📁 **Полные логи:** `{self.messages_log}`"
            else:
                logs_text = "📄 Логи пока пусты. Напиши что-нибудь!"
            
            await update.message.reply_text(logs_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка чтения логов: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "help")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/help", "command")
        
        help_text = """🔧 **LLMStruct Chat Bot - Команды**

**📊 Мониторинг:**
/status - Статус системы
/metrics - Детальные метрики
/dev - Информация для разработчиков

**🤖 Взаимодействие с Cursor:**
/cursor - Информация о логировании
/logs - Показать последние сообщения

**💬 Общение:**
Просто пиши мне вопросы! Я понимаю:
• Вопросы о проекте и коде
• Просьбы о помощи с разработкой
• Обсуждение архитектуры
• Команды для Cursor/Claude

**🎯 Примеры команд для Cursor:**
"Cursor, покажи статус системы"
"Claude, исправь проблемы с ботом"
"Продолжи работу над API"

**📈 Метрики:** """ + ("✅ Включены" if METRICS_AVAILABLE else "❌ Отключены") + """
**📝 Логирование:** ✅ Активно
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        task_id = f"chat_bot_status_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "chat_bot_status_check")
            track_workflow_event("bot_command", "status")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/status", "command")
        
        try:
            # Проверка API
            api_status = "❌ Недоступен"
            try:
                import requests
                response = requests.get("http://localhost:8000/api/v1/system/health", timeout=2)
                if response.status_code == 200:
                    api_status = "✅ Работает"
            except:
                pass
            
            # Проверка struct.json
            struct_file = Path("struct.json")
            struct_status = "❌ Отсутствует"
            if struct_file.exists():
                age_hours = (time.time() - struct_file.stat().st_mtime) / 3600
                if age_hours < 1:
                    struct_status = "✅ Актуальный"
                elif age_hours < 6:
                    struct_status = "🟡 Недавний"
                else:
                    struct_status = "⚠️ Устаревший"
            
            # Проверка логов
            logs_status = "✅ Активно" if self.messages_log.exists() else "❌ Не настроено"
            cursor_logs_count = 0
            if self.cursor_commands.exists():
                with open(self.cursor_commands, 'r', encoding='utf-8') as f:
                    cursor_logs_count = len(f.readlines())
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            status_text = f"""📊 **Статус LLMStruct System**

🌐 **API Server:** {api_status}
📁 **struct.json:** {struct_status}
📊 **Metrics:** {"✅ Активны" if METRICS_AVAILABLE else "❌ Отключены"}
🤖 **Chat Bot:** ✅ Работает
📝 **Логирование:** {logs_status}
🎯 **Команды Cursor:** {cursor_logs_count} записей
⏰ **Время:** {current_time}

🔄 **Последнее обновление:** только что
"""
            
            if METRICS_AVAILABLE:
                # Добавляем краткие метрики
                try:
                    tracker = get_metrics_tracker()
                    summary = tracker.get_session_summary()
                    status_text += f"""
📈 **Текущая сессия:**
• ID: `{summary['session_id'][:8]}`
• Время: {summary['duration']:.0f}s
• Токены: {summary['total_tokens']:,}
• Эффективность: {summary['efficiency_score']:.2f}/1.0
"""
                    track_task_complete(task_id, "success")
                except Exception as e:
                    status_text += f"\n⚠️ *Ошибка метрик: {str(e)[:50]}*"
            
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
        except Exception as e:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", str(e))
            await update.message.reply_text(f"❌ Ошибка получения статуса: {e}")
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /metrics"""
        if not METRICS_AVAILABLE:
            await update.message.reply_text("❌ Система метрик недоступна")
            return
        
        track_workflow_event("bot_command", "metrics")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/metrics", "command")
        
        try:
            tracker = get_metrics_tracker()
            summary = tracker.get_session_summary()
            
            efficiency_emoji = "🟢" if summary['efficiency_score'] > 0.8 else "🟡" if summary['efficiency_score'] > 0.6 else "🔴"
            
            metrics_text = f"""📊 **Детальные метрики**
**Сессия:** `{summary['session_id'][:8]}`

{efficiency_emoji} **Эффективность:** {summary['efficiency_score']:.2f}/1.0
⏱ **Время работы:** {summary['duration']:.0f}s ({summary['duration']/60:.1f}m)
🔢 **Токены:** {summary['total_tokens']:,}
💰 **Стоимость:** ${summary['estimated_cost']:.4f}

📋 **Задачи:**
• Выполнено: {summary['tasks_completed']}/{summary['tasks_total']}
• Повторы: {summary['retries']}
• Ошибки: {summary['avoidable_errors']}

🛤 **Проблемы:**
• Ложные пути: {summary['false_paths']}

📝 **Логирование:**
• Сообщения: ✅ Активно
• Файл: `{self.messages_log}`

📈 **Рекомендации:**
"""
            
            if summary['efficiency_score'] < 0.7:
                metrics_text += "⚠️ Низкая эффективность - проверьте паттерны работы\n"
            elif summary['efficiency_score'] > 0.9:
                metrics_text += "🎉 Отличная эффективность!\n"
            else:
                metrics_text += "✅ Хорошая эффективность\n"
                
            if summary['false_paths'] > 5:
                metrics_text += "🔍 Много ложных путей - уточняйте задачи\n"
                
            if summary['avoidable_errors'] > 0:
                metrics_text += "⚡ Есть предотвратимые ошибки - проверьте настройки\n"
            
            await update.message.reply_text(metrics_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения метрик: {e}")
    
    async def dev_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /dev - информация для разработчиков"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "dev")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/dev", "command")
        
        dev_text = f"""🔧 **Developer Information**

**🎯 Проект:** LLMStruct AI-Enhanced Development Environment
**📂 Репозиторий:** Локальная разработка
**🐍 Python:** 3.8+ с виртуальным окружением

**🚀 Доступные сервисы:**
• CLI: `python -m llmstruct.cli`
• API: `python test_api_simple.py`
• Metrics: `python -m llmstruct.cli metrics`

**📊 Файлы проекта:**
• `struct.json` - структура проекта
• `.metrics/` - данные метрик
• `src/llmstruct/` - основной код

**📝 Логирование Telegram:**
• Все сообщения: `{self.messages_log}`
• Команды Cursor: `{self.cursor_commands}`
• Статус: ✅ Активно

**🤖 Bot Status:**
• Token: ✅ Активен
• Metrics: """ + ("✅ Включены" if METRICS_AVAILABLE else "❌ Отключены") + """
• Mode: Chat/Development + Cursor Integration

**💡 Useful Commands:**
`git status`, `python -m llmstruct.cli metrics status`

**🎯 Cursor Integration:**
Все сообщения логируются и доступны для чтения AI ассистентом!
"""
        
        await update.message.reply_text(dev_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Улучшенная обработка текстовых сообщений с логированием"""
        task_id = f"chat_bot_message_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "chat_bot_conversation")
            track_workflow_event("bot_command", "chat_message")
        
        # Логируем сообщение пользователя
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, update.message.text, "text")
        
        user_message = update.message.text.lower()
        user_name = update.effective_user.first_name
        
        try:
            # Интеллектуальный анализ сообщения
            response = ""
            
            # Специальная обработка команд для Cursor
            if any(keyword in user_message for keyword in ['cursor', 'claude']):
                response = f"""🤖 **Команда для Cursor зафиксирована!**

Ваше сообщение записано в логи:
📄 `logs/telegram/user_messages.log`
📄 `logs/telegram/cursor_commands.log`

Cursor может теперь прочитать: "{update.message.text}"

Используйте команды:
• "Cursor, покажи статус"
• "Claude, исправь проблему"
• "Продолжи работу с ботом"
"""
                
            elif any(word in user_message for word in ["привет", "hello", "hi", "здравствуй"]):
                response = f"👋 Привет, {user_name}! Как дела с разработкой? Все твои сообщения теперь логируются для Cursor! 📝"
                
            elif any(word in user_message for word in ["метрики", "metrics", "статистика"]):
                await self.metrics_command(update, context)
                return
                
            elif any(word in user_message for word in ["статус", "status", "состояние"]):
                await self.status_command(update, context)
                return
                
            elif any(word in user_message for word in ["помощь", "help", "команды"]):
                await self.help_command(update, context)
                return
                
            elif any(word in user_message for word in ["логи", "logs", "сообщения"]):
                await self.logs_command(update, context)
                return
                
            elif any(word in user_message for word in ["проект", "project", "llmstruct"]):
                response = """🧠 **О проекте LLMStruct:**

Это AI-Enhanced Development Environment с самоанализом возможностей:
• 📊 Система объективных метрик
• 🤖 AI интеграция с контекстными режимами  
• 🔄 Workflow management
• 📁 Автоматический анализ структуры проекта
• 📝 **НОВОЕ**: Логирование для Cursor

Хочешь узнать что-то конкретное?"""
                
            elif any(word in user_message for word in ["код", "code", "разработка", "development"]):
                response = """💻 **Помощь с кодом:**

Могу помочь с:
• 🔍 Анализом структуры проекта
• 📊 Мониторингом метрик разработки
• 🛠 Отладкой и оптимизацией
• 📝 Документированием кода
• 🤖 **НОВОЕ**: Передачей команд Cursor'у

Расскажи конкретнее, что нужно сделать? Или обратись напрямую к Cursor!"""
                
            elif any(word in user_message for word in ["как дела", "how are you", "как работаешь"]):
                if METRICS_AVAILABLE:
                    tracker = get_metrics_tracker()
                    summary = tracker.get_session_summary()
                    efficiency = summary['efficiency_score']
                    if efficiency > 0.8:
                        response = f"🎉 Отлично! Эффективность {efficiency:.2f}, всё работает как часы! И теперь логирую для Cursor! 📝"
                    elif efficiency > 0.6:
                        response = f"😊 Хорошо! Эффективность {efficiency:.2f}, есть к чему стремиться. Логи для Cursor активны! 📝"
                    else:
                        response = f"🤔 Так себе... Эффективность {efficiency:.2f}, надо улучшать. Может Cursor поможет? 📝"
                else:
                    response = "😊 Работаю нормально! Метрики не подключены, но логирую все сообщения для Cursor! 📝"
                    
            elif any(word in user_message for word in ["спасибо", "thanks", "thank you"]):
                response = f"🙏 Пожалуйста, {user_name}! Всегда рад помочь с разработкой! Все логируется для Cursor! 📝"
                
            elif any(word in user_message for word in ["пока", "bye", "goodbye", "до свидания"]):
                response = f"👋 До свидания, {user_name}! Удачи с проектом! Логи сохранены для Cursor! 📝"
                
            else:
                # Общий ответ для неопознанных сообщений
                response = f"""🤔 Интересный вопрос, {user_name}!

📝 **Сообщение записано:** "{update.message.text[:100]}{'...' if len(update.message.text) > 100 else ''}"

**💬 Могу помочь с:**
• 📊 Метриками проекта (/metrics)
• 🔍 Статусом системы (/status)  
• 💻 Вопросами о коде и разработке
• 🛠 Настройкой и отладкой
• 🤖 Передачей команд Cursor'у (/cursor)

**💡 Или обратись к Cursor напрямую:**
"Cursor, помоги с этим вопросом"
"Claude, что думаешь об этом?"

Все сообщения логируются! 📄"""
            
            if METRICS_AVAILABLE and response:
                # Трекинг "токенов" для сообщения
                input_tokens = len(update.message.text.split())
                output_tokens = len(response.split())
                tracker = get_metrics_tracker()
                tracker.track_token_usage("telegram_chat_bot", "conversation", input_tokens, output_tokens)
                track_task_complete(task_id, "success")
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", str(e))
            await update.message.reply_text(f"❌ Ошибка обработки сообщения: {e}")
    
    def run_sync(self):
        """Синхронный запуск бота"""
        try:
            # Установка команд бота
            commands = [
                BotCommand("start", "🚀 Начать работу"),
                BotCommand("help", "❓ Показать помощь"),
                BotCommand("status", "📊 Статус системы"),
                BotCommand("metrics", "📈 Детальные метрики"),
                BotCommand("dev", "🔧 Информация для разработчиков"),
                BotCommand("cursor", "🤖 Взаимодействие с Cursor"),
                BotCommand("logs", "📄 Показать последние сообщения"),
            ]
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.application.bot.set_my_commands(commands))
            
            logger.info("🤖 Starting LLMStruct Chat Bot...")
            if METRICS_AVAILABLE:
                tracker = get_metrics_tracker()
                logger.info(f"📊 Metrics session: {tracker.session_data['session_id']}")
            
            # Запуск бота
            self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            if METRICS_AVAILABLE:
                track_workflow_event("bot_error", str(e))
        finally:
            if METRICS_AVAILABLE:
                track_workflow_event("chat_bot_shutdown")
                tracker = get_metrics_tracker()
                tracker.save_session()
                logger.info("📊 Metrics saved")

def main():
    """Главная функция"""
    # Получение токена бота
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Telegram bot token not found!")
        print("Set with: export TELEGRAM_BOT_TOKEN='your_token'")
        return
    
    # Создание и запуск бота
    bot = LLMStructChatBot(token)
    bot.run_sync()

if __name__ == "__main__":
    main() 