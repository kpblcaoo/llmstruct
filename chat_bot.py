#!/usr/bin/env python3
"""
LLMStruct Chat Bot - Улучшенная версия для взаимодействия с Cursor + Ollama
"""

import os
import json
import time
import logging
import aiohttp
import toml
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
    from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event, track_task_start, track_task_complete, track_token_usage
    METRICS_AVAILABLE = True
    logger.info("📊 Metrics system loaded")
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("⚠️ Metrics system not available")

class LLMStructChatBot:
    """Улучшенный чат-бот для LLMStruct с логированием для Cursor + Ollama"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Настройка файлов для логирования
        self.logs_dir = Path("logs/telegram")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл для логирования сообщений (читаемый Cursor'ом)
        self.messages_log = self.logs_dir / "user_messages.log"
        self.cursor_commands = self.logs_dir / "cursor_commands.log"
        
        # Загрузка конфигурации Ollama
        self.load_ollama_config()
        
        self.setup_handlers()
        
        if METRICS_AVAILABLE:
            track_workflow_event("chat_bot_startup")
    
    def load_ollama_config(self):
        """Загружает конфигурацию Ollama из llmstruct.toml"""
        try:
            config_path = Path("llmstruct.toml")
            if config_path.exists():
                config = toml.load(config_path)
                # Читаем из правильной секции [api]
                self.ollama_host = config.get("api", {}).get("ollama_host", "http://localhost:11434")
                # Используем mistral по умолчанию (он есть у пользователя)
                self.ollama_model = config.get("api", {}).get("model", "mistral:latest")
                logger.info(f"🦙 Ollama config loaded: {self.ollama_host}, model: {self.ollama_model}")
            else:
                # Fallback конфигурация
                self.ollama_host = "http://192.168.88.50:11434"
                self.ollama_model = "mistral:latest"
                logger.warning(f"⚠️ Config file not found, using defaults: {self.ollama_host}, model: {self.ollama_model}")
                
            # Список доступных моделей
            self.available_models = [
                "mistral:latest",
                "deepseek-coder:6.7b-instruct", 
                "deepseek-coder:6.7b",
                "nomic-embed-text:latest"
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to load Ollama config: {e}")
            # Fallback значения
            self.ollama_host = "http://192.168.88.50:11434"
            self.ollama_model = "mistral:latest"
            self.available_models = ["mistral:latest"]
    
    async def query_ollama(self, message: str, context: str = "") -> str:
        """Отправляет запрос к Ollama и получает ответ"""
        try:
            prompt = f"""Ты - LLMStruct AI Assistant, работающий через Telegram бот.
            
Контекст: {context if context else "Обычный разговор"}

Пользователь: {message}

Отвечай на русском языке, будь полезным и дружелюбным. Если вопрос касается разработки, программирования или LLMStruct проекта - давай подробные технические ответы."""

            data = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_host}/api/generate", json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ollama_response = result.get("response", "").strip()
                        
                        if METRICS_AVAILABLE:
                            # Трекинг токенов
                            input_tokens = len(message.split())
                            output_tokens = len(ollama_response.split())
                            tracker = get_metrics_tracker()
                            tracker.track_token_usage("ollama", self.ollama_model, input_tokens, output_tokens)
                        
                        return ollama_response
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ollama error {response.status}: {error_text}")
                        return f"❌ Ошибка Ollama: {response.status}"
                        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Ollama error: {error_msg}")
            
            if "timeout" in error_msg.lower():
                return "⏰ Ollama не отвечает (timeout 30s)"
            elif "connection" in error_msg.lower() or "cannot connect" in error_msg.lower():
                return f"🌐 Не могу подключиться к Ollama: {error_msg}"
            else:
                return f"❌ Ошибка при обращении к Ollama: {error_msg}"
    
    def log_user_message(self, user_info: dict, message: str, message_type: str = "text", chat_id: int = None):
        """Логирует сообщения пользователя в читаемый файл для Cursor"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""
=== {timestamp} ===
👤 USER: {user_info.get('first_name', 'Unknown')} (@{user_info.get('username', 'unknown')})
📱 TYPE: {message_type}
🆔 CHAT_ID: {chat_id if chat_id else 'unknown'}
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
        self.application.add_handler(CommandHandler("ollama", self.ollama_command))
        self.application.add_handler(CommandHandler("model", self.model_command))
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
        self.log_user_message(user_info, "/start", "command", update.effective_chat.id)
        
        user_name = update.effective_user.first_name
        welcome_message = f"""👋 Привет, {user_name}!

🧠 Я **LLMStruct Chat Bot** - теперь с Ollama! 🦙

**🎯 Новые возможности:**
• 🦙 **Ollama AI** - умные ответы на русском языке
• 🔄 **Выбор модели** - переключайся между моделями
• 📝 Логирую все сообщения для Cursor'а
• 🤖 Взаимодействие с AI ассистентом
• 📊 Полная интеграция с метриками
• 🔧 Режим разработчика

**📋 Команды:**
/help - все команды
/status - статус системы
/metrics - метрики проекта
/ollama - статус Ollama сервера
/model - выбор модели ({len(self.available_models)} доступно)
/cursor - взаимодействие с Cursor
/logs - показать последние сообщения
/dev - режим разработчика

**💬 Режимы работы:**
1. **Умный диалог** - просто пиши сообщения, отвечу через Ollama! 🧠
2. **Команды для Cursor** - используй: "cursor", "claude", "продолжи", "исправь"
3. **Выбор модели** - используй /model и выбери номер модели

🦙 **Текущая модель:** `{self.ollama_model}`
🌐 **Сервер:** `{self.ollama_host}`

📱 **Доступные модели:**
{chr(10).join([f"  {i+1}. {model}" for i, model in enumerate(self.available_models)])}

Все твои сообщения логируются в `logs/telegram/user_messages.log` 📄"""
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
        self.log_user_message(user_info, "/cursor", "command", update.effective_chat.id)
        
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
        self.log_user_message(user_info, "/logs", "command", update.effective_chat.id)
        
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
        self.log_user_message(user_info, "/help", "command", update.effective_chat.id)
        
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
        self.log_user_message(user_info, "/status", "command", update.effective_chat.id)
        
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
        self.log_user_message(user_info, "/metrics", "command", update.effective_chat.id)
        
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
        self.log_user_message(user_info, "/dev", "command", update.effective_chat.id)
        
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
    
    async def ollama_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /ollama - проверка связи с Ollama"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "ollama")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/ollama", "command", update.effective_chat.id)
        
        await update.message.reply_text("🔍 Проверяю связь с Ollama...")
        
        try:
            # Проверка доступности Ollama
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        model_names = [m.get("name", "unknown") for m in models]
                        
                        ollama_text = f"""🦙 **Ollama Status**

🟢 **Сервер:** `{self.ollama_host}` - ✅ Доступен
🤖 **Текущая модель:** `{self.ollama_model}`

📋 **Доступные модели:**"""
                        
                        for model in model_names[:5]:  # Показываем первые 5
                            status = "✅" if model == self.ollama_model else "⚪"
                            ollama_text += f"\n• {status} `{model}`"
                        
                        if len(model_names) > 5:
                            ollama_text += f"\n• ... и ещё {len(model_names) - 5} моделей"
                        
                        if not model_names:
                            ollama_text += "\n⚠️ Нет установленных моделей"
                        
                        # Тестовый запрос
                        test_response = await self.query_ollama("Привет! Это тест связи.")
                        if not test_response.startswith("❌"):
                            ollama_text += f"""\n\n🧪 **Тест связи:** ✅ Успешно
📝 **Ответ:** {test_response[:100]}{'...' if len(test_response) > 100 else ''}"""
                        else:
                            ollama_text += f"\n\n🧪 **Тест связи:** ❌ {test_response}"
                    
                    else:
                        ollama_text = f"""🦙 **Ollama Status**

🔴 **Сервер:** `{self.ollama_host}` - ❌ Недоступен
📊 **Код ошибки:** {response.status}

💡 **Решения:**
• Проверьте что Ollama запущен
• Убедитесь что адрес правильный
• Проверьте firewall/сеть"""
            
            await update.message.reply_text(ollama_text, parse_mode='Markdown')
            
        except Exception as e:
            error_text = f"""🦙 **Ollama Status**

🔴 **Сервер:** `{self.ollama_host}` - ❌ Ошибка подключения
⚠️ **Ошибка:** {str(e)}

💡 **Возможные причины:**
• Ollama не запущен
• Неверный адрес сервера  
• Проблемы с сетью
• Timeout соединения"""
            
            await update.message.reply_text(error_text, parse_mode='Markdown')
    
    async def model_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /model - переключение между моделями Ollama"""
        if METRICS_AVAILABLE:
            track_workflow_event("bot_command", "model")
        
        # Логируем команду
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        self.log_user_message(user_info, "/model", "command", update.effective_chat.id)
        
        await update.message.reply_text("🤔 Выберите модель Ollama:")
        
        model_options = "\n".join([f"{i+1}. {model}" for i, model in enumerate(self.available_models)])
        await update.message.reply_text(model_options, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Улучшенная обработка текстовых сообщений с Ollama + логирование"""
        task_id = f"chat_bot_message_{int(time.time())}"
        
        if METRICS_AVAILABLE:
            track_task_start(task_id, "chat_bot_conversation")
            track_workflow_event("bot_command", "chat_message")
        
        # Логируем сообщение пользователя
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        
        # Проверяем на ответ (reply)
        reply_context = ""
        if update.message.reply_to_message:
            original_text = update.message.reply_to_message.text or ""
            reply_context = f"Ответ на: {original_text[:100]}..."
        
        message_text = update.message.text
        self.log_user_message(user_info, message_text, "text", update.effective_chat.id)
        
        # Проверяем выбор модели по номеру
        if message_text.isdigit():
            model_num = int(message_text) - 1
            if 0 <= model_num < len(self.available_models):
                old_model = self.ollama_model
                self.ollama_model = self.available_models[model_num]
                
                if METRICS_AVAILABLE:
                    track_token_usage("ollama", self.ollama_model, 2, 35)
                    track_task_complete(task_id, "success")
                    
                await update.message.reply_text(
                    f"✅ **Модель изменена**\n\n"
                    f"Было: `{old_model}`\n"
                    f"Стало: `{self.ollama_model}`\n\n"
                    f"🦙 Теперь все сообщения будут обрабатываться через {self.ollama_model}",
                    parse_mode='Markdown'
                )
                return
        
        # Проверяем команды для Cursor
        cursor_keywords = ["cursor", "claude", "продолжи", "исправь", "помоги", "проанализируй"]
        is_cursor_command = any(keyword in message_text.lower() for keyword in cursor_keywords)
        
        if is_cursor_command:
            # Записываем как команду для Cursor
            cursor_log = f"logs/telegram/cursor_commands.log"
            Path(cursor_log).parent.mkdir(parents=True, exist_ok=True)
            
            with open(cursor_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                f.write(f"\n============================================================\n")
                f.write(f"📅 {timestamp}\n")
                f.write(f"👤 {user_info['first_name']}\n")
                if reply_context:
                    f.write(f"🎯 {reply_context}\n")
                f.write(f"📝 {message_text}\n")
                f.write(f"============================================================\n")
            
            if METRICS_AVAILABLE:
                track_token_usage("cursor", "command", len(message_text.split()), 30)
                track_task_complete(task_id, "success")
                
            await update.message.reply_text(f"⚙️ **Cursor AI обработал команду**\n\n📝 `{message_text[:100]}{'...' if len(message_text) > 100 else ''}`\n\n✅ Задача передана разработчику", parse_mode='Markdown')
            return
        
        # Обычное сообщение - отправляем в Ollama
        try:
            context_info = f"Контекст: {reply_context}" if reply_context else "Обычный разговор"
            response = await self.query_ollama(message_text, context_info)
            
            if METRICS_AVAILABLE:
                track_token_usage("ollama", self.ollama_model, len(message_text.split()), len(response.split()))
                track_task_complete(task_id, "success")
                
            # Убираем parse_mode чтобы избежать 400 Bad Request из-за Markdown символов
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "failed")
                
            await update.message.reply_text(f"❌ Ошибка обработки сообщения: {str(e)}")
    
    def run_sync(self):
        """Синхронный запуск бота"""
        try:
            # Установка команд бота
            commands = [
                BotCommand("start", "🚀 Начать работу"),
                BotCommand("help", "❓ Показать помощь"),
                BotCommand("status", "📊 Статус системы"),
                BotCommand("metrics", "📈 Детальные метрики"),
                BotCommand("ollama", "🦙 Статус Ollama сервера"),
                BotCommand("model", "🔄 Выбор модели"),
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