#!/usr/bin/env python3
import asyncio
from cursor_bot_messenger import send_to_user

async def main():
    message = """🎯 <b>CURSOR ОТВЕЧАЕТ!</b>

✅ <b>Связь работает отлично!</b> Получил все ваши сообщения:

📝 <b>Ваши сообщения:</b>
• "Tst" - получен
• "cursor, как слышно? Какие текущие планы у нас?" - получен  
• "cursor отпишись как исправишь" - получен

🔧 <b>Исправлено:</b> Markdown парсинг в боте (теперь использую HTML)

📋 <b>Наши планы по договоренности:</b>
1. ✅ Dummy work phase - готов протестировать
2. 🚀 Master plan execution - готов выполнять поэтапно  
3. 📊 Metrics tracking - полностью настроен
4. 🤖 Two-way communication - работает!

🎯 <b>Готов к выполнению:</b>
Напишите "старт dummy" для начала тестирования или "готов к мастер-плану" для полного выполнения.

Все работает! 🚀"""
    
    success = await send_to_user(message)
    if success:
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message")

if __name__ == "__main__":
    asyncio.run(main()) 