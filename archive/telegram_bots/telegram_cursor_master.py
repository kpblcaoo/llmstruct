#!/usr/bin/env python3
"""
🎯 LLMStruct Telegram Master Controller
Единое решение для seamless управления мастер-планом через Telegram

Архитектура:
- Один стабильный Telegram Bot  
- File-based communication с Cursor
- Clear command protocols
- Real-time status updates
"""

import os
import sys
import json
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

import httpx
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramCursorMaster:
    """Мастер-контроллер для управления через Telegram"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        self.user_chat_id = -4938821563  # Your chat ID
        
        # Communication files
        self.commands_file = Path("data/telegram/cursor_commands.json")
        self.responses_file = Path("data/telegram/cursor_responses.json") 
        self.status_file = Path("data/telegram/master_status.json")
        
        # Ensure directories exist
        self.commands_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup handlers
        self.setup_handlers()
        
        # Initialize status
        self.update_status("🚀 Master Controller Started", "ready")
        
        logger.info("🎯 Telegram Cursor Master initialized")
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        
        # Commands
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("master", self.cmd_master))
        self.application.add_handler(CommandHandler("stop", self.cmd_stop))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        
        # Messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        message = """🎯 **LLMStruct Master Controller**

🚀 **Управление мастер-планом через Telegram**

**Команды:**
• `/master` - Запустить мастер-план
• `/status` - Статус выполнения  
• `/stop` - Остановить выполнение
• `/help` - Справка

**Режимы сообщений:**
• Обычное сообщение → команда для Cursor
• Reply на мое сообщение → продолжение диалога

✅ Готов к работе!"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("📱 Start command processed")
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command"""
        status = self.read_status()
        
        message = f"""📊 **Статус мастер-контроллера**

🎯 **Текущий статус:** {status.get('status', 'unknown')}
📝 **Последнее сообщение:** {status.get('message', 'N/A')}
⏰ **Обновлено:** {status.get('timestamp', 'N/A')}

🔧 **Активные процессы:**
• Telegram Bot: ✅ Работает
• File Watcher: ✅ Активен  
• Cursor Integration: ✅ Готов

💾 **Файлы коммуникации:**
• Commands: `{self.commands_file}`
• Responses: `{self.responses_file}`
• Status: `{self.status_file}`"""

        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("📊 Status command processed")
    
    async def cmd_master(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Master plan command"""
        
        # Send command to Cursor
        command = {
            "id": f"master_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "user": update.effective_user.username or "Unknown",
            "command": "start_master_plan",
            "args": " ".join(context.args) if context.args else "",
            "chat_id": update.effective_chat.id,
            "message_id": update.message.message_id
        }
        
        self.write_command(command)
        self.update_status("🚀 Мастер-план запускается...", "executing")
        
        message = """🚀 **МАСТЕР-ПЛАН ЗАПУЩЕН**

⚙️ **Команда отправлена Cursor AI**
📝 **ID команды:** `{}`
⏳ **Ожидание обработки...**

📊 Cursor AI начнет выполнение и будет отчитываться здесь о прогрессе.

🔄 Используй `/status` для проверки статуса""".format(command['id'])
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"🎯 Master plan command sent: {command['id']}")
    
    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop command"""
        
        command = {
            "id": f"stop_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "user": update.effective_user.username or "Unknown", 
            "command": "stop_execution",
            "chat_id": update.effective_chat.id,
            "message_id": update.message.message_id
        }
        
        self.write_command(command)
        self.update_status("🛑 Остановка выполнения...", "stopping")
        
        await update.message.reply_text(
            "🛑 **Команда остановки отправлена**\n\n⏳ Ожидание подтверждения от Cursor AI...",
            parse_mode='Markdown'
        )
        
        logger.info(f"🛑 Stop command sent: {command['id']}")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        message = """📖 **Справка по управлению**

🎯 **Основные команды:**
• `/master [args]` - Запуск мастер-плана  
• `/status` - Текущий статус
• `/stop` - Остановить выполнение
• `/help` - Эта справка

💬 **Взаимодействие с Cursor:**
• Любое сообщение → команда для Cursor AI
• Reply на сообщение бота → продолжение диалога
• Cursor отвечает автоматически через этот чат

🔧 **Протокол выполнения:**
1. Отправляешь команду
2. Cursor получает и обрабатывает  
3. Cursor отчитывается о прогрессе
4. Ты можешь корректировать процесс

⚡ **Seamless workflow** для максимального удобства!"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        
        message_text = update.message.text
        is_reply = update.message.reply_to_message is not None
        
        # Create command for Cursor
        command = {
            "id": f"msg_{int(time.time())}",
            "timestamp": datetime.now().isoformat(), 
            "user": update.effective_user.username or "Unknown",
            "command": "user_message",
            "message": message_text,
            "is_reply": is_reply,
            "chat_id": update.effective_chat.id,
            "message_id": update.message.message_id
        }
        
        if is_reply:
            command["reply_to_text"] = update.message.reply_to_message.text
        
        self.write_command(command)
        
        # Send acknowledgment
        if is_reply:
            ack_text = "💬 **Ответ передан Cursor AI**\n\n⏳ Обрабатываю..."
        else:
            ack_text = "🎯 **Команда передана Cursor AI**\n\n⏳ Обрабатываю..."
        
        await update.message.reply_text(ack_text, parse_mode='Markdown')
        
        logger.info(f"📝 Message processed: {command['id']}")
    
    def write_command(self, command: Dict):
        """Write command to file for Cursor"""
        try:
            commands = []
            if self.commands_file.exists():
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
            
            commands.append(command)
            
            # Keep only last 100 commands
            if len(commands) > 100:
                commands = commands[-100:]
            
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(commands, f, ensure_ascii=False, indent=2)
                
            logger.info(f"📝 Command written: {command['id']}")
            
        except Exception as e:
            logger.error(f"❌ Error writing command: {e}")
    
    def read_status(self) -> Dict:
        """Read current status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error reading status: {e}")
        
        return {"status": "unknown", "message": "N/A", "timestamp": "N/A"}
    
    def update_status(self, message: str, status: str):
        """Update status file"""
        try:
            status_data = {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"📊 Status updated: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error updating status: {e}")
    
    async def start_response_watcher(self):
        """Start watching for responses from Cursor"""
        logger.info("👁️ Starting response watcher...")
        
        last_check = 0
        while True:
            try:
                if self.responses_file.exists():
                    stat = self.responses_file.stat()
                    if stat.st_mtime > last_check:
                        last_check = stat.st_mtime
                        await self.process_responses()
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"❌ Response watcher error: {e}")
                await asyncio.sleep(5)
    
    async def process_responses(self):
        """Process responses from Cursor"""
        try:
            with open(self.responses_file, 'r', encoding='utf-8') as f:
                responses = json.load(f)
            
            for response in responses:
                if not response.get('sent', False):
                    await self.send_response(response)
                    response['sent'] = True
            
            # Write back with sent flags
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error processing responses: {e}")
    
    async def send_response(self, response: Dict):
        """Send response to Telegram"""
        try:
            message = response.get('message', 'No message')
            
            await self.bot.send_message(
                chat_id=self.user_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📤 Response sent: {response.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
    
    async def run(self):
        """Run the master controller"""
        
        # Set bot commands
        commands = [
            ("start", "Запустить контроллер"),
            ("master", "Запустить мастер-план"),
            ("status", "Проверить статус"),
            ("stop", "Остановить выполнение"),
            ("help", "Справка")
        ]
        await self.bot.set_my_commands(commands)
        
        logger.info("🚀 Starting Telegram Cursor Master...")
        
        # Start response watcher as background task
        asyncio.create_task(self.start_response_watcher())
        
        # Start the bot
        await self.application.run_polling(drop_pending_updates=True)

def main():
    """Main function"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found!")
        return 1
    
    try:
        master = TelegramCursorMaster(token)
        
        # Use existing event loop if available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create new loop for this task
                import threading
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(master.run())
                    new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.daemon = True
                thread.start()
                thread.join()
            else:
                loop.run_until_complete(master.run())
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(master.run())
            
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 