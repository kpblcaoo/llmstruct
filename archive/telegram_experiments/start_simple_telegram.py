#!/usr/bin/env python3
"""
Скрипт запуска базового решения Cursor ↔ Telegram
Простое и надежное решение без сложностей
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def check_token():
    """Проверка наличия токена"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        print("Set it with: export TELEGRAM_BOT_TOKEN='your_token'")
        return False
    
    print(f"✅ Token found: {token[:10]}...{token[-10:]}")
    return True

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import requests
        print("✅ requests library OK")
        return True
    except ImportError:
        print("❌ requests library not found!")
        print("Install with: pip install requests")
        return False

def start_bot():
    """Запуск простого бота"""
    print("🚀 Starting Simple Telegram Bot...")
    
    if not check_token():
        return False
    
    if not check_dependencies():
        return False
    
    # Запускаем бот
    try:
        process = subprocess.Popen([
            sys.executable, "simple_telegram_bot.py"
        ], cwd=Path.cwd())
        
        print(f"✅ Bot started with PID: {process.pid}")
        print("📱 Bot is now active in Telegram!")
        print("🔧 Available Cursor commands:")
        print("  python cursor_simple_integration.py test      - Test integration")
        print("  python cursor_simple_integration.py send 'Hi' - Send message")
        print("  python cursor_simple_integration.py monitor   - Monitor messages")
        print("\nPress Ctrl+C to stop the bot")
        
        # Ждем сигнала остановки
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Bot stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        return False

def test_integration():
    """Тест интеграции"""
    print("🧪 Testing Cursor ↔ Telegram integration...")
    
    try:
        from cursor_simple_integration import test_integration
        return test_integration()
    except ImportError:
        print("❌ cursor_simple_integration.py not found")
        return False

def show_status():
    """Показать статус системы"""
    try:
        from cursor_simple_integration import show_conversation_status, list_recent_messages
        
        print("📊 System Status:")
        status = show_conversation_status()
        
        print(f"  👤 User messages: {status.get('total_user_messages', 0)}")
        print(f"  🤖 Cursor commands: {status.get('total_cursor_commands', 0)}")
        print(f"  ⏳ Pending commands: {status.get('pending_commands', 0)}")
        
        if status.get('last_user_message'):
            msg = status['last_user_message']
            print(f"  💬 Last message: {msg.get('text', '')[:50]}...")
        
        print("\n📬 Recent messages:")
        list_recent_messages(3)
        
        return True
        
    except ImportError:
        print("❌ Integration module not found")
        return False

def main():
    """Главная функция"""
    print("🎯 Simple Telegram Bot Manager")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Commands:")
        print("  start    - Start the telegram bot")
        print("  test     - Test integration")
        print("  status   - Show system status")
        print("")
        print("Example: python start_simple_telegram.py start")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "start":
        success = start_bot()
        return 0 if success else 1
    
    elif command == "test":
        success = test_integration()
        return 0 if success else 1
    
    elif command == "status":
        success = show_status()
        return 0 if success else 1
    
    else:
        print(f"❌ Unknown command: {command}")
        return 1

if __name__ == "__main__":
    exit(main()) 