#!/usr/bin/env python3
"""
Enhanced LLMStruct Telegram Bot
- Smart reply detection (reply_to_message support)
- LLM chain: Ollama → Grok → Anthropic
- Cursor command forwarding to Cursor AI
- Concise responses by default
"""

import os
import sys
import json
import time
import asyncio
import logging
import signal
from datetime import datetime
from typing import Optional, Dict, Any

import httpx
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event, track_task_start, track_task_complete, track_token_usage
    METRICS_AVAILABLE = True
except ImportError:
    print("⚠️ Metrics system not available")
    METRICS_AVAILABLE = False

class EnhancedLLMStructChatBot:
    """Enhanced Telegram bot with LLM chain and smart reply detection"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.app = None
        
        # LLM chain configuration
        self.ollama_base = "http://192.168.88.50:11434"
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        # Cursor integration
        self.cursor_chat_id = None  # Will be detected from first cursor message
        self.user_chat_id = None    # Primary user chat ID
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Message logging
        os.makedirs("logs/telegram", exist_ok=True)
        self.message_log_file = "logs/telegram/user_messages.log"
        self.cursor_log_file = "logs/telegram/cursor_commands.log"
        
        if METRICS_AVAILABLE:
            self.metrics = get_metrics_tracker()
            track_workflow_event("chat_bot_startup")
            self.logger.info(f"📊 Metrics session: {self.metrics.session_data.get('session_id', 'unknown')}")
        else:
            self.metrics = None

    def log_user_message(self, user_info: dict, message: str, message_type: str = "text", chat_id: int = None, reply_to_message: dict = None):
        """Log user message with reply context"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.message_log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== {timestamp} ===\n")
            f.write(f"👤 USER: {user_info.get('first_name', 'Unknown')} (@{user_info.get('username', 'no_username')})\n")
            f.write(f"📱 TYPE: {message_type}\n")
            if chat_id:
                f.write(f"🆔 CHAT_ID: {chat_id}\n")
            if reply_to_message:
                f.write(f"↩️ REPLY_TO: {reply_to_message.get('text', 'N/A')[:50]}...\n")
            f.write(f"💬 MESSAGE: {message}\n")
            f.write("=" * 60 + "\n")

    def log_cursor_command(self, message: str, user_info: dict, reply_context: str = ""):
        """Log cursor command for processing"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.cursor_log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== CURSOR COMMAND {timestamp} ===\n")
            f.write(f"👤 FROM: {user_info.get('first_name', 'Unknown')}\n")
            f.write(f"🎯 COMMAND: {message}\n")
            if reply_context:
                f.write(f"📝 CONTEXT: {reply_context}\n")
            f.write("=" * 60 + "\n")

    async def ollama_chat(self, message: str, model: str = "llama3.1") -> Optional[str]:
        """Try Ollama first"""
        try:
            url = f"{self.ollama_base}/api/generate"
            data = {
                "model": model,
                "prompt": f"Отвечай кратко и по делу (1-3 предложения максимум):\n{message}",
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
        except Exception as e:
            self.logger.warning(f"Ollama failed: {e}")
        return None

    async def grok_chat(self, message: str) -> Optional[str]:
        """Fallback to Grok"""
        if not self.grok_api_key:
            return None
            
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": "Отвечай кратко и полезно. Максимум 2-3 предложения."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150
            }
            
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            self.logger.warning(f"Grok failed: {e}")
        return None

    async def anthropic_chat(self, message: str) -> Optional[str]:
        """Final fallback to Anthropic"""
        if not self.anthropic_key:
            return None
            
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.anthropic_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 150,
                "system": "Отвечай кратко и по существу. Максимум 2-3 предложения.",
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
            
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"].strip()
        except Exception as e:
            self.logger.warning(f"Anthropic failed: {e}")
        return None

    async def llm_chain_response(self, message: str) -> str:
        """LLM chain: Ollama → Grok → Anthropic"""
        
        # Try Ollama first
        response = await self.ollama_chat(message)
        if response:
            return f"🦙 {response}"
        
        # Fallback to Grok
        response = await self.grok_chat(message)
        if response:
            return f"🚀 {response}"
            
        # Final fallback to Anthropic
        response = await self.anthropic_chat(message)
        if response:
            return f"🧠 {response}"
            
        # If all fail
        return "❌ Все LLM провайдеры недоступны. Попробуйте позже."

    def setup_handlers(self):
        """Setup bot handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        
        # Message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        return self.app

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Set user chat ID for the primary user
        if not self.user_chat_id:
            self.user_chat_id = chat_id
        
        response = """🤖 *Enhanced LLMStruct Bot*

*LLM Chain:* 🦙 Ollama → 🚀 Grok → 🧠 Anthropic

*Commands:*
• Обычное сообщение → LLM chain (краткие ответы)
• `cursor <команда>` → передача в Cursor AI
• Ответ на сообщение бота → автоматически cursor режим

*Features:*
✅ Умная детекция ответов
✅ Краткие полезные ответы  
✅ Интеграция с Cursor
✅ Метрики и логирование

Готов к работе! 🚀"""

        await update.message.reply_text(response, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """📚 *Справка по Enhanced Bot*

*Основные режимы:*
• Обычное сообщение → LLM chain
• `cursor команда` → Cursor AI
• Ответ на сообщение бота → Cursor AI

*LLM Chain приоритет:*
1️⃣ 🦙 Ollama (192.168.88.50) - быстро и локально
2️⃣ 🚀 Grok - умно и креативно  
3️⃣ 🧠 Anthropic - надежный fallback

*Особенности:*
• Краткие ответы (1-3 предложения)
• Автоматическая детекция контекста
• Логирование всех взаимодействий
• Метрики производительности

Ready! 🎯"""

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command"""
        status_parts = ["🔍 *System Status*\n"]
        
        # Check Ollama
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_base}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    status_parts.append(f"🦙 Ollama: ✅ ({len(models)} models)")
                else:
                    status_parts.append("🦙 Ollama: ❌")
        except:
            status_parts.append("🦙 Ollama: ❌")
        
        # Check other services
        status_parts.append(f"🚀 Grok: {'✅' if self.grok_api_key else '❌'}")
        status_parts.append(f"🧠 Anthropic: {'✅' if self.anthropic_key else '❌'}")
        
        if METRICS_AVAILABLE and self.metrics:
            status_parts.append(f"📊 Metrics: ✅ (session: {self.metrics.session_data.get('session_id', 'unknown')[:8]})")
        else:
            status_parts.append("📊 Metrics: ❌")
            
        await update.message.reply_text("\n".join(status_parts), parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all text messages with smart routing"""
        user = update.effective_user
        message = update.message
        text = message.text.strip()
        chat_id = update.effective_chat.id
        
        # Track metrics
        if METRICS_AVAILABLE and self.metrics:
            task_id = f"chat_bot_message_{int(time.time())}"
            track_task_start(task_id, "chat_bot_conversation")
            track_workflow_event("bot_message")
        
        # Log message with reply context
        reply_to_message = None
        if message.reply_to_message:
            reply_to_message = {
                "text": message.reply_to_message.text,
                "from_bot": message.reply_to_message.from_user.is_bot
            }
        
        self.log_user_message(
            user_info=user.to_dict(),
            message=text,
            chat_id=chat_id,
            reply_to_message=reply_to_message
        )
        
        # Determine routing
        is_cursor_command = False
        cursor_message = text
        
        # Check for explicit cursor command
        if text.lower().startswith("cursor"):
            is_cursor_command = True
            cursor_message = text[6:].strip() if len(text) > 6 else "status"
            
        # Check for reply to bot message (auto-cursor mode)
        elif (reply_to_message and reply_to_message.get("from_bot", False)):
            is_cursor_command = True
            cursor_message = f"Ответ на: {reply_to_message['text'][:50]}...\nМой ответ: {text}"
        
        try:
            if is_cursor_command:
                # Log cursor command
                reply_context = reply_to_message.get("text", "") if reply_to_message else ""
                self.log_cursor_command(cursor_message, user.to_dict(), reply_context)
                
                # Send acknowledgment
                response = f"🎯 *Команда передана в Cursor AI*\n\n`{cursor_message[:100]}{'...' if len(cursor_message) > 100 else ''}`\n\n⏳ Обрабатываю..."
                await message.reply_text(response, parse_mode='Markdown')
                
                # Track tokens for cursor command
                if METRICS_AVAILABLE:
                    input_tokens = len(cursor_message.split())
                    output_tokens = len(response.split()) 
                    track_token_usage("telegram", "cursor", input_tokens, output_tokens)
                    
            else:
                # Regular LLM chain
                response = await self.llm_chain_response(text)
                await message.reply_text(response, parse_mode='Markdown')
                
                # Track tokens for LLM response
                if METRICS_AVAILABLE:
                    input_tokens = len(text.split())
                    output_tokens = len(response.split())
                    track_token_usage("telegram", "llm_chain", input_tokens, output_tokens)
            
            # Complete task tracking
            if METRICS_AVAILABLE and self.metrics:
                track_task_complete(task_id, "success")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_msg = "❌ Произошла ошибка при обработке сообщения"
            await message.reply_text(error_msg)
            
            if METRICS_AVAILABLE and self.metrics:
                track_task_complete(task_id, "failed")

    def run_sync(self, timeout_minutes: int = 10):
        """Run bot synchronously with timeout"""
        shutdown_requested = False
        
        def signal_handler(signum, frame):
            nonlocal shutdown_requested
            self.logger.info(f"🛑 Received signal {signum}, shutting down...")
            shutdown_requested = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            app = self.setup_handlers()
            
            self.logger.info("🤖 Starting Enhanced LLMStruct Chat Bot...")
            self.logger.info(f"⏰ Will run for {timeout_minutes} minutes max")
            if METRICS_AVAILABLE and self.metrics:
                self.logger.info(f"📊 Metrics session: {self.metrics.session_data.get('session_id', 'unknown')}")
            
            # Start time for timeout
            start_time = time.time()
            timeout_seconds = timeout_minutes * 60
            
            # Create async runner with timeout
            async def run_with_timeout():
                nonlocal shutdown_requested
                application = app
                await application.initialize()
                await application.start()
                await application.updater.start_polling(drop_pending_updates=True)
                
                # Check for timeout or shutdown signal periodically
                while not shutdown_requested:
                    await asyncio.sleep(1)
                    
                    if time.time() - start_time > timeout_seconds:
                        self.logger.info(f"⏰ Timeout reached ({timeout_minutes} minutes)")
                        break
                
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
            
            # Run the bot
            try:
                asyncio.run(run_with_timeout())
            except RuntimeError as e:
                if "This event loop is already running" in str(e):
                    self.logger.warning("⚠️ Event loop already running, using current loop")
                    loop = asyncio.get_event_loop()
                    task = loop.create_task(run_with_timeout())
                    loop.run_until_complete(task)
                else:
                    raise
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Bot error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if METRICS_AVAILABLE:
                track_workflow_event("chat_bot_shutdown")
                self.logger.info("📊 Metrics saved")
            self.logger.info("✅ Bot shutdown complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced LLMStruct Telegram Bot")
    parser.add_argument("--timeout", "-t", type=int, default=10, 
                       help="Bot timeout in minutes (default: 10)")
    parser.add_argument("--foreground", "-f", action="store_true",
                       help="Run in foreground mode")
    
    args = parser.parse_args()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return 1
    
    print(f"🚀 Starting Enhanced Bot (timeout: {args.timeout}min)")
    bot = EnhancedLLMStructChatBot(token)
    bot.run_sync(timeout_minutes=args.timeout)
    return 0

if __name__ == "__main__":
    exit(main()) 