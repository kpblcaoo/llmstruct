#!/usr/bin/env python3
"""
Test message sender to Telegram
Отправляет тестовое сообщение и ждет ответа от пользователя
"""

import os
import sys
import asyncio
import httpx
from datetime import datetime

async def send_test_message():
    """Отправляет тестовое сообщение в Telegram"""
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7576808324:AAG_lyXEt-AEfGCSJ5VoOx1oUEniyjcmHBI")
    chat_id = -4938821563  # Your chat ID from logs
    
    test_message = """🧪 **ТЕСТ ДВУСТОРОННЕЙ СВЯЗИ**

📱 Cursor → Telegram: **РАБОТАЕТ** ✅
🔄 Сейчас тестируем: Telegram → Cursor

**Задача:** Ответь любым сообщением для проверки связи
📝 Например: "тест", "ok", "работает" или что угодно

⏳ Жду твоего ответа (без таймаута)
🤖 Cursor будет ждать, пока ты не ответишь"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": test_message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                print("✅ Тестовое сообщение отправлено в Telegram!")
                print(f"📱 Chat ID: {chat_id}")
                print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
                print("\n🔄 Теперь жду твоего ответа в Telegram...")
                print("📝 Ответь любым сообщением для проверки связи")
                print("\n💡 Курсор будет ждать здесь, пока ты не ответишь")
                return True
            else:
                print(f"❌ Ошибка отправки: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def wait_for_user_response():
    """Ждет ответа пользователя через мониторинг логов"""
    
    user_log_file = "logs/telegram/user_messages.log"
    
    # Получаем текущее время для отслеживания новых сообщений
    start_time = datetime.now()
    print(f"\n⏰ Начинаю ожидание с {start_time.strftime('%H:%M:%S')}")
    
    while True:
        try:
            if os.path.exists(user_log_file):
                with open(user_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Ищем новые сообщения после start_time
                for line in reversed(lines[-10:]):  # Последние 10 строк
                    if "| Михаил (@kpblcko_mike):" in line:
                        # Извлекаем время из лога
                        try:
                            timestamp_str = line.split(" | ")[0]
                            log_time = datetime.fromisoformat(timestamp_str.replace("T", " "))
                            
                            if log_time > start_time:
                                # Новое сообщение!
                                message = line.split("): ", 1)[1].strip()
                                print(f"\n🎉 ПОЛУЧЕН ОТВЕТ!")
                                print(f"⏰ Время: {log_time.strftime('%H:%M:%S')}")
                                print(f"💬 Сообщение: '{message}'")
                                print("\n✅ ДВУСТОРОННЯЯ СВЯЗЬ РАБОТАЕТ!")
                                return message
                        except:
                            continue
            
            # Ждем 1 секунду перед следующей проверкой
            await asyncio.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⏹️ Остановлено пользователем")
            return None
        except Exception as e:
            print(f"❌ Ошибка при ожидании: {e}")
            await asyncio.sleep(2)

async def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТ ДВУСТОРОННЕЙ СВЯЗИ CURSOR ↔ TELEGRAM")
    print("=" * 50)
    
    # Отправляем тестовое сообщение
    if await send_test_message():
        # Ждем ответа
        response = await wait_for_user_response()
        
        if response:
            print(f"\n🎯 РЕЗУЛЬТАТ ТЕСТА: УСПЕХ")
            print(f"📝 Полученный ответ: '{response}'")
            print("✅ Связь Cursor ↔ Telegram работает корректно!")
        else:
            print(f"\n❌ РЕЗУЛЬТАТ ТЕСТА: НЕ ЗАВЕРШЕН")
    else:
        print("❌ Не удалось отправить тестовое сообщение")

if __name__ == "__main__":
    asyncio.run(main()) 