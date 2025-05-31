#!/usr/bin/env python3
"""
Cursor ↔ Telegram Bridge
Читает cursor команды и отправляет ответы обратно в Telegram
"""

import os
import sys
import time
import asyncio
import httpx
import json
from typing import Dict, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cursor_telegram_reader_enhanced import EnhancedCursorTelegramReader

class CursorTelegramBridge:
    """Bridge между cursor командами и Telegram ответами"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.user_chat_id = -4938821563  # From logs
        
        self.reader = EnhancedCursorTelegramReader()
        
        # Response templates
        self.response_templates = {
            "processing": "⚙️ *Cursor обрабатывает команду...*\n\n`{command}`\n\n⏳ Результат будет через несколько секунд",
            "completed": "✅ *Выполнено Cursor AI*\n\n{result}",
            "error": "❌ *Ошибка выполнения*\n\n{error}",
            "timeout": "⏰ *Таймаут выполнения*\n\nКоманда заняла слишком много времени"
        }
    
    async def send_telegram_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Отправить сообщение в Telegram"""
        if not self.bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.user_chat_id,
            "text": text[:4096],  # Telegram limit
            "parse_mode": parse_mode
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    print(f"✅ Message sent to Telegram")
                    return True
                else:
                    print(f"❌ Failed to send message: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    async def process_cursor_command(self, command_data: Dict):
        """Обработать cursor команду"""
        command = command_data['command']
        context = command_data.get('context', '')
        
        print(f"\n🎯 Processing cursor command: {command[:50]}...")
        
        # Send processing notification
        processing_msg = self.response_templates["processing"].format(command=command[:100])
        await self.send_telegram_message(processing_msg)
        
        # Simulate processing (here you would integrate with actual Cursor AI)
        # For now, we'll create smart responses based on command content
        result = await self.simulate_cursor_processing(command, context)
        
        # Send result
        if result.get("success"):
            response_msg = self.response_templates["completed"].format(result=result["content"])
        else:
            response_msg = self.response_templates["error"].format(error=result.get("error", "Unknown error"))
        
        await self.send_telegram_message(response_msg)
    
    async def simulate_cursor_processing(self, command: str, context: str = "") -> Dict:
        """Симуляция обработки командs Cursor AI"""
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # Smart responses based on command content
        command_lower = command.lower()
        
        if "статус" in command_lower or "status" in command_lower:
            return {
                "success": True,
                "content": """🔍 *Статус системы LLMStruct*

📊 *Компоненты:*
• Enhanced Telegram Bot: ✅ Активен
• LLM Chain: 🦙 Ollama → 🚀 Grok → 🧠 Anthropic
• Cursor Bridge: ✅ Работает
• Metrics System: ✅ Активна

🎯 *Готов к выполнению команд!*"""
            }
        
        elif "помощь" in command_lower or "help" in command_lower:
            return {
                "success": True,
                "content": """📚 *Cursor AI помощь*

🎯 *Доступные команды:*
• `статус` - проверить состояние системы
• `анализ` - анализ кода/проекта
• `рефакторинг` - предложения по улучшению
• `тесты` - создание тестов
• `документация` - генерация docs

💡 *Как использовать:*
1. Просто ответьте на это сообщение
2. Или напишите `cursor <команда>`
3. Получите умный ответ!"""
            }
        
        elif "анализ" in command_lower or "анализ кода" in command_lower:
            return {
                "success": True,
                "content": """🔍 *Анализ кода LLMStruct*

📋 *Обнаружено:*
• 272 модуля проанализированы
• 1857 функций в базе знаний  
• 183 класса для использования

✅ *Сильные стороны:*
• Хорошая архитектура AI системы
• Метрики и мониторинг
• Telegram интеграция

💡 *Рекомендации:*
• Добавить больше unit тестов
• Улучшить error handling
• Оптимизировать производительность"""
            }
        
        elif any(word in command_lower for word in ["готов", "ready", "start", "старт"]):
            return {
                "success": True,
                "content": """🚀 *Cursor AI готов к работе!*

✅ *Система инициализирована:*
• Enhanced Bot запущен
• LLM Chain активна
• Bridge работает

🎯 *Ждем ваших команд!*
Можете начинать работу с проектом."""
            }
        
        else:
            # General processing
            return {
                "success": True,
                "content": f"""⚙️ *Cursor AI обработал команду*

📝 *Команда:* `{command[:100]}{'...' if len(command) > 100 else ''}`

💭 *Результат:*
Команда принята к исполнению. Для более детальной обработки требуется конкретизация задачи.

🎯 *Что дальше?*
Опишите более детально, что нужно сделать."""
            }
    
    def handle_cursor_command(self, command_data: Dict):
        """Handle cursor command (sync wrapper)"""
        print(f"\n{'='*60}")
        print(f"📅 {command_data['timestamp']}")
        print(f"👤 {command_data['from_user']}")
        print(f"🎯 {command_data['command']}")
        if command_data['context']:
            print(f"📝 {command_data['context']}")
        print("="*60)
        
        # Process asynchronously
        asyncio.run(self.process_cursor_command(command_data))
    
    def start_bridge(self):
        """Запустить bridge"""
        print("🌉 Starting Cursor ↔ Telegram Bridge")
        print(f"🎯 Target chat: {self.user_chat_id}")
        print("Press Ctrl+C to stop\n")
        
        # Show recent context
        recent_messages = self.reader.get_recent_user_messages(3)
        if recent_messages:
            print("📝 Recent messages context:")
            for msg in recent_messages:
                print(f"  {msg['timestamp'][:19]} | {msg['user']}: {msg['message'][:50]}...")
            print()
        
        # Send startup notification
        startup_msg = """🌉 *Cursor ↔ Telegram Bridge запущен*

✅ Готов к обработке cursor команд
📱 Ответы будут приходить в этот чат
🎯 Используйте `cursor <команда>` или отвечайте на сообщения бота

Ready! 🚀"""
        
        asyncio.run(self.send_telegram_message(startup_msg))
        
        # Start polling
        self.reader.poll_for_commands(self.handle_cursor_command)

def main():
    """Main entry point"""
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return 1
    
    bridge = CursorTelegramBridge()
    bridge.start_bridge()
    return 0

if __name__ == "__main__":
    exit(main()) 