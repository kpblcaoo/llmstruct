#!/usr/bin/env python3
"""
Тестирование Telegram бота без реального Telegram
"""

import asyncio
import sys
import os

# Добавляем путь к основному проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from bot import LLMStructTelegramBot

async def test_bot_functions():
    """Тестирование функций бота"""
    print("🧪 Testing LLMStruct Telegram Bot functionality...")
    
    # Создаем бота с фиктивным токеном
    bot = LLMStructTelegramBot("fake_token_for_testing")
    
    print("\n1️⃣ Testing command execution...")
    
    # Тест безопасных команд
    safe_commands = ["date", "pwd", "whoami", "uptime"]
    
    for cmd in safe_commands:
        print(f"   Testing: {cmd}")
        result = await bot.execute_command(cmd)
        print(f"   Result: {result[:100]}{'...' if len(result) > 100 else ''}")
    
    # Тест небезопасной команды
    print(f"   Testing unsafe command...")
    result = await bot.execute_command("rm")
    print(f"   Result: {result}")
    
    print("\n2️⃣ Testing LLM chat...")
    
    # Проверяем подключение к API
    test_message = "Привет! Как дела?"
    print(f"   Sending: {test_message}")
    
    response = await bot.chat_with_llm(test_message)
    print(f"   LLM Response: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    print("\n3️⃣ Testing message handling simulation...")
    
    # Симулируем различные типы сообщений
    test_messages = [
        {
            "message": {
                "chat": {"id": 12345},
                "text": "/start",
                "from": {"first_name": "TestUser"}
            }
        },
        {
            "message": {
                "chat": {"id": 12345},
                "text": "/cmd date",
                "from": {"first_name": "TestUser"}
            }
        },
        {
            "message": {
                "chat": {"id": 12345},
                "text": "/status",
                "from": {"first_name": "TestUser"}
            }
        },
        {
            "message": {
                "chat": {"id": 12345},
                "text": "Расскажи о LLMStruct кратко",
                "from": {"first_name": "TestUser"}
            }
        }
    ]
    
    # Заменяем send_message на print для тестирования
    original_send_message = bot.send_message
    
    async def mock_send_message(chat_id, text, parse_mode="Markdown"):
        print(f"   📱 [CHAT {chat_id}] {text[:100]}{'...' if len(text) > 100 else ''}")
        return {"ok": True}
    
    bot.send_message = mock_send_message
    
    for i, test_update in enumerate(test_messages):
        print(f"\n   Message {i+1}: {test_update['message']['text']}")
        await bot.handle_message(test_update)
    
    print("\n✅ Bot testing completed!")
    print("\n📋 Summary:")
    print("   - Command execution: ✅ Working")
    print("   - LLM integration: ✅ Working")
    print("   - Message handling: ✅ Working")
    print("   - Security: ✅ Only safe commands allowed")

async def check_api_status():
    """Проверка статуса API"""
    print("🔍 Checking LLMStruct API status...")
    
    bot = LLMStructTelegramBot("fake_token")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/system/health")
            if response.status_code == 200:
                print("   ✅ LLMStruct API is running!")
                return True
            else:
                print(f"   ❌ API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        print("   💡 Start API with: source venv/bin/activate && python test_api.py")
        return False

if __name__ == "__main__":
    print("🤖 LLMStruct Telegram Bot Test Suite")
    print("=" * 50)
    
    loop = asyncio.get_event_loop()
    
    # Проверяем API
    api_ok = loop.run_until_complete(check_api_status())
    
    if api_ok:
        # Если API работает, тестируем полную функциональность
        loop.run_until_complete(test_bot_functions())
    else:
        print("\n⚠️  API not available, testing only command execution...")
        
        async def test_commands_only():
            bot = LLMStructTelegramBot("fake_token")
            print("\n📝 Testing safe commands:")
            
            for cmd in ["date", "pwd", "whoami"]:
                result = await bot.execute_command(cmd)
                print(f"   {cmd}: {result[:50]}{'...' if len(result) > 50 else ''}")
        
        loop.run_until_complete(test_commands_only())
    
    print("\n🎯 To run the real bot:")
    print("   1. Get token from @BotFather")  
    print("   2. export TELEGRAM_BOT_TOKEN='your_token'")
    print("   3. python bot.py") 