#!/usr/bin/env python3
"""
Cursor Bot Messenger - Отправка сообщений пользователю через Telegram
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime

try:
    from telegram import Bot
    import asyncio
except ImportError:
    print("❌ Missing telegram dependencies. Install with: pip install python-telegram-bot")
    exit(1)

class CursorBotMessenger:
    """Класс для отправки сообщений из Cursor в Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        
        self.bot = Bot(token=self.bot_token)
        # ID чата пользователя (нужно получить при первом запуске)
        self.user_chat_id = None
        self.logs_dir = Path("logs/telegram")
        
    async def get_user_chat_id(self):
        """Получение chat_id пользователя из логов"""
        messages_log = self.logs_dir / "user_messages.log"
        if messages_log.exists():
            try:
                with open(messages_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем последний chat_id
                lines = content.split('\n')
                for line in reversed(lines):
                    if 'CHAT_ID:' in line:
                        chat_id = line.split('CHAT_ID:')[1].strip()
                        self.user_chat_id = int(chat_id)
                        return self.user_chat_id
            except Exception as e:
                print(f"❌ Error reading chat_id: {e}")
        
        return None
    
    async def send_message(self, message: str, parse_mode: str = "Markdown"):
        """Отправка сообщения пользователю"""
        if not self.user_chat_id:
            await self.get_user_chat_id()
        
        if not self.user_chat_id:
            print("❌ User chat_id not found. User needs to send a message to the bot first.")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.user_chat_id,
                text=message,
                parse_mode=parse_mode
            )
            print(f"✅ Message sent to user: {message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    async def wait_for_user_response(self, timeout_minutes: int = 10):
        """Ожидание ответа пользователя"""
        print(f"⏳ Waiting for user response (timeout: {timeout_minutes} minutes)...")
        
        # Записываем маркер времени последней проверки
        start_time = time.time()
        last_check_time = datetime.now()
        
        messages_log = self.logs_dir / "user_messages.log"
        
        while (time.time() - start_time) < (timeout_minutes * 60):
            if messages_log.exists():
                try:
                    with open(messages_log, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Ищем новые сообщения после last_check_time
                    entries = content.split('===')
                    for entry in reversed(entries):
                        if entry.strip():
                            lines = entry.strip().split('\n')
                            if len(lines) >= 4:
                                timestamp_str = lines[0].strip()
                                try:
                                    # Парсим timestamp
                                    msg_time = datetime.fromisoformat(timestamp_str)
                                    if msg_time > last_check_time:
                                        message_text = lines[3].replace('💬 MESSAGE:', '').strip()
                                        print(f"📨 User response received: {message_text}")
                                        return message_text
                                except:
                                    continue
                except Exception as e:
                    print(f"❌ Error reading messages: {e}")
            
            await asyncio.sleep(2)  # Проверяем каждые 2 секунды
        
        print("⏱️ Timeout waiting for user response")
        return None

async def send_to_user(message: str):
    """Удобная функция для отправки сообщения"""
    messenger = CursorBotMessenger()
    return await messenger.send_message(message)

async def wait_for_response(timeout_minutes: int = 10):
    """Удобная функция для ожидания ответа"""
    messenger = CursorBotMessenger()
    return await messenger.wait_for_user_response(timeout_minutes)

async def interactive_communication(question: str, timeout_minutes: int = 10):
    """Отправить вопрос и дождаться ответа"""
    messenger = CursorBotMessenger()
    
    # Отправляем вопрос
    success = await messenger.send_message(f"❓ **Cursor Question:**\n\n{question}")
    if not success:
        return None
    
    # Ждем ответ
    response = await messenger.wait_for_user_response(timeout_minutes)
    return response

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cursor_bot_messenger.py <message>")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    
    async def main():
        await send_to_user(message)
    
    asyncio.run(main()) 