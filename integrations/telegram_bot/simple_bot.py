#!/usr/bin/env python3
"""
Упрощенный Telegram бот для LLMStruct с интеграцией метрик
Без сложных зависимостей, основная функциональность
"""

import os
import json
import time
import asyncio
import logging
from typing import Optional

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
    sys.path.append('../..')
    from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event, track_task_start, track_task_complete
    METRICS_AVAILABLE = True
    logger.info("📊 Metrics system loaded")
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("⚠️ Metrics system not available")

class SimpleLLMStructBot:
    """Упрощенный Telegram бот для LLMStruct"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        if METRICS_AVAILABLE:
            track_workflow_event("bot_startup")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("metrics", self.metrics_command))
        self.application.add_handler(CommandHandler("struct", self.struct_command))
        self.application.add_handler(CommandHandler("parse", self.parse_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "start")
        
        welcome_message = """🧠 LLMStruct Bot - Упрощенная версия

Доступные команды:
/help - Показать все команды
/status - Статус системы 
/metrics - Метрики проекта
/struct - Статус struct.json
/parse - Обновить struct.json

Просто напишите сообщение для анализа или вопроса о проекте!
"""
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "help")
        
        help_text = """🔧 **LLMStruct Bot Commands**

**📊 Мониторинг:**
/status - Системный статус
/metrics - Метрики текущей сессии
/struct - Состояние struct.json

**🛠 Workflow:**
/parse - Обновить struct.json
Просто текст - Анализ/вопрос о проекте

**📈 Метрики включены:** """ + ("✅" if METRICS_AVAILABLE else "❌")
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        task_id = f"bot_status_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "bot_status_check")
            track_workflow_event("bot_command", "status")
        
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
            from pathlib import Path
            struct_file = Path("../../struct.json")
            struct_status = "❌ Отсутствует"
            if struct_file.exists():
                age_hours = (time.time() - struct_file.stat().st_mtime) / 3600
                if age_hours < 1:
                    struct_status = "✅ Актуальный"
                elif age_hours < 6:
                    struct_status = "🟡 Недавний"
                else:
                    struct_status = "⚠️ Устаревший"
            
            status_text = f"""📊 **Статус LLMStruct**

🌐 **API:** {api_status}
📁 **struct.json:** {struct_status}
📊 **Метрики:** {"✅ Активны" if METRICS_AVAILABLE else "❌ Отключены"}
🤖 **Бот:** ✅ Работает
⏰ **Время:** {time.strftime("%H:%M:%S")}
"""
            
            if METRICS_AVAILABLE:
                # Добавляем краткие метрики
                tracker = get_metrics_tracker()
                summary = tracker.get_session_summary()
                status_text += f"""
📈 **Текущая сессия:**
- ID: {summary['session_id'][:8]}
- Время: {summary['duration']:.0f}s
- Токены: {summary['total_tokens']}
- Эффективность: {summary['efficiency_score']:.2f}
"""
                track_task_complete(task_id, "success")
            
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
        
        try:
            tracker = get_metrics_tracker()
            summary = tracker.get_session_summary()
            
            metrics_text = f"""📊 **Метрики сессии {summary['session_id'][:8]}**

⏱ **Время:** {summary['duration']:.0f}s ({summary['duration']/60:.1f}m)
🎯 **Эффективность:** {summary['efficiency_score']:.2f}/1.0
🔢 **Токены:** {summary['total_tokens']:,}
💰 **Стоимость:** ${summary['estimated_cost']:.4f}

📋 **Задачи:** {summary['tasks_completed']}/{summary['tasks_total']}
🔄 **Повторы:** {summary['retries']}
⚠️ **Ошибки:** {summary['avoidable_errors']}

🛤 **Ложные пути:** {summary['false_paths']}
"""
            
            if summary['efficiency_score'] < 0.7:
                metrics_text += "\n⚠️ *Низкая эффективность - проверьте паттерны работы*"
            
            await update.message.reply_text(metrics_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения метрик: {e}")
    
    async def struct_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /struct"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "struct")
        
        try:
            from pathlib import Path
            struct_file = Path("../../struct.json")
            
            if not struct_file.exists():
                await update.message.reply_text("❌ struct.json не найден. Используйте /parse для создания.")
                return
            
            stat = struct_file.stat()
            size_kb = stat.st_size / 1024
            modified = time.ctime(stat.st_mtime)
            age_hours = (time.time() - stat.st_mtime) / 3600
            
            status_emoji = "✅" if age_hours < 1 else "🟡" if age_hours < 6 else "⚠️"
            
            struct_text = f"""📁 **struct.json Status**

{status_emoji} **Статус:** {"Актуальный" if age_hours < 1 else "Устаревший" if age_hours > 6 else "Недавний"}
📏 **Размер:** {size_kb:.1f} KB
📅 **Изменен:** {modified}
⏰ **Возраст:** {age_hours:.1f} часов

{"ℹ️ *Рекомендуется обновить*" if age_hours > 6 else "✅ *Файл актуален*"}
"""
            
            await update.message.reply_text(struct_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка проверки struct.json: {e}")
    
    async def parse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /parse"""
        task_id = f"bot_parse_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "bot_struct_update")
            track_workflow_event("bot_command", "parse")
        
        await update.message.reply_text("🔄 Обновляю struct.json...")
        
        try:
            import subprocess
            import os
            
            # Меняем директорию на корень проекта
            os.chdir("../..")
            
            # Запускаем обновление struct.json
            result = subprocess.run(
                ["python", "-m", "llmstruct.cli", "parse", ".", "-o", "struct.json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if METRICS_AVAILABLE:
                    track_workflow_event("struct_json_used")
                    track_task_complete(task_id, "success")
                
                await update.message.reply_text("✅ struct.json успешно обновлен!")
            else:
                if METRICS_AVAILABLE:
                    track_task_complete(task_id, "failed", "CLI command failed")
                
                await update.message.reply_text(f"❌ Ошибка обновления:\n```\n{result.stderr}\n```", parse_mode='Markdown')
        
        except subprocess.TimeoutExpired:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", "Timeout")
            await update.message.reply_text("❌ Превышено время ожидания обновления")
        
        except Exception as e:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", str(e))
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        task_id = f"bot_message_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "bot_text_processing")
            track_workflow_event("bot_command", "text_message")
        
        user_message = update.message.text
        
        try:
            # Простой анализ сообщения
            if "метрики" in user_message.lower() or "metrics" in user_message.lower():
                await self.metrics_command(update, context)
                return
            
            if "статус" in user_message.lower() or "status" in user_message.lower():
                await self.status_command(update, context)
                return
            
            if "struct" in user_message.lower():
                await self.struct_command(update, context)
                return
            
            # Базовый ответ
            response = f"""🤖 Получено сообщение: "{user_message[:50]}..."

Доступные команды:
- /status - Статус системы
- /metrics - Метрики проекта  
- /struct - Информация о struct.json
- /parse - Обновить struct.json

Или используйте ключевые слова: "метрики", "статус", "struct"
"""
            
            if METRICS_AVAILABLE:
                # Трекинг "токенов" для сообщения
                input_tokens = len(user_message.split())
                output_tokens = len(response.split())
                tracker = get_metrics_tracker()
                tracker.track_token_usage("telegram_bot", "simple_echo", input_tokens, output_tokens)
                track_task_complete(task_id, "success")
            
            await update.message.reply_text(response)
            
        except Exception as e:
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed", str(e))
            await update.message.reply_text(f"❌ Ошибка обработки сообщения: {e}")
    
    def run_sync(self):
        """Синхронный запуск бота"""
        try:
            # Установка команд бота
            commands = [
                BotCommand("start", "Начать работу с ботом"),
                BotCommand("help", "Показать помощь"),
                BotCommand("status", "Статус системы"),
                BotCommand("metrics", "Метрики проекта"),
                BotCommand("struct", "Статус struct.json"),
                BotCommand("parse", "Обновить struct.json"),
            ]
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.application.bot.set_my_commands(commands))
            
            logger.info("🤖 Starting LLMStruct Simple Bot...")
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
                track_workflow_event("bot_shutdown")
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
    bot = SimpleLLMStructBot(token)
    bot.run_sync()

if __name__ == "__main__":
    main() 