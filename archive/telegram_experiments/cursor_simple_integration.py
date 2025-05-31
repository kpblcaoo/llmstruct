#!/usr/bin/env python3
"""
Простые функции интеграции Cursor с Telegram ботом
Базовое решение через JSON файлы без сложностей
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Директория для обмена данными
DATA_DIR = Path("data/telegram")
USER_MESSAGES_FILE = DATA_DIR / "user_messages.json"
CURSOR_COMMANDS_FILE = DATA_DIR / "cursor_commands.json"
BOT_RESPONSES_FILE = DATA_DIR / "bot_responses.json"

def ensure_data_dir():
    """Создание директории для данных"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Инициализация файлов если их нет
    for file in [USER_MESSAGES_FILE, CURSOR_COMMANDS_FILE, BOT_RESPONSES_FILE]:
        if not file.exists():
            file.write_text('[]')

def get_user_messages(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Получение последних сообщений пользователя
    
    Args:
        limit: Количество последних сообщений (по умолчанию 10)
    
    Returns:
        Список последних сообщений пользователя
    """
    ensure_data_dir()
    
    try:
        with open(USER_MESSAGES_FILE, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        # Возвращаем последние сообщения
        return messages[-limit:] if messages else []
        
    except Exception as e:
        print(f"❌ Error reading user messages: {e}")
        return []

def send_to_telegram(text: str, message_type: str = "response") -> bool:
    """
    Отправка сообщения в Telegram через бота
    
    Args:
        text: Текст сообщения
        message_type: Тип сообщения (response, notification, etc.)
    
    Returns:
        True если сообщение успешно добавлено в очередь
    """
    ensure_data_dir()
    
    try:
        # Читаем существующие команды
        with open(CURSOR_COMMANDS_FILE, 'r', encoding='utf-8') as f:
            commands = json.load(f)
        
        # Добавляем новую команду
        new_command = {
            "id": f"cmd_{int(time.time())}_{len(commands)}",
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "type": message_type,
            "processed": False
        }
        
        commands.append(new_command)
        
        # Оставляем только последние 50 команд
        if len(commands) > 50:
            commands = commands[-50:]
        
        # Сохраняем
        with open(CURSOR_COMMANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(commands, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Message queued for Telegram: {text[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return False

def check_new_messages(last_check_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Проверка новых сообщений пользователя с определенного времени
    
    Args:
        last_check_timestamp: ISO timestamp последней проверки
    
    Returns:
        Список новых сообщений
    """
    ensure_data_dir()
    
    try:
        with open(USER_MESSAGES_FILE, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if not last_check_timestamp:
            # Если не указано время, возвращаем последнее сообщение
            return messages[-1:] if messages else []
        
        # Фильтруем сообщения после указанного времени
        new_messages = []
        for msg in messages:
            if msg.get("timestamp", "") > last_check_timestamp:
                new_messages.append(msg)
        
        return new_messages
        
    except Exception as e:
        print(f"❌ Error checking new messages: {e}")
        return []

def get_last_message() -> Optional[Dict[str, Any]]:
    """
    Получение последнего сообщения пользователя
    
    Returns:
        Последнее сообщение или None
    """
    messages = get_user_messages(limit=1)
    return messages[0] if messages else None

def show_conversation_status() -> Dict[str, Any]:
    """
    Получение статуса текущего разговора
    
    Returns:
        Статус разговора с метриками
    """
    ensure_data_dir()
    
    try:
        # Читаем сообщения пользователя
        with open(USER_MESSAGES_FILE, 'r', encoding='utf-8') as f:
            user_messages = json.load(f)
        
        # Читаем команды Cursor
        with open(CURSOR_COMMANDS_FILE, 'r', encoding='utf-8') as f:
            cursor_commands = json.load(f)
        
        # Находим последние сообщения
        last_user_msg = user_messages[-1] if user_messages else None
        pending_commands = [cmd for cmd in cursor_commands if not cmd.get("processed", False)]
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_user_messages": len(user_messages),
            "total_cursor_commands": len(cursor_commands),
            "pending_commands": len(pending_commands),
            "last_user_message": last_user_msg,
            "bot_active": Path("simple_bot.log").exists(),
            "data_files": {
                "user_messages": USER_MESSAGES_FILE.exists(),
                "cursor_commands": CURSOR_COMMANDS_FILE.exists(),
                "bot_responses": BOT_RESPONSES_FILE.exists()
            }
        }
        
        return status
        
    except Exception as e:
        print(f"❌ Error getting conversation status: {e}")
        return {"error": str(e)}

def start_conversation_monitor(callback_func=None, check_interval: int = 3):
    """
    Запуск мониторинга новых сообщений
    
    Args:
        callback_func: Функция для обработки новых сообщений
        check_interval: Интервал проверки в секундах
    """
    ensure_data_dir()
    
    print("🔍 Starting conversation monitor...")
    print("Press Ctrl+C to stop")
    
    last_timestamp = datetime.now().isoformat()
    
    try:
        while True:
            new_messages = check_new_messages(last_timestamp)
            
            if new_messages:
                print(f"\n📝 {len(new_messages)} new message(s):")
                for msg in new_messages:
                    print(f"  👤 {msg.get('username', 'Unknown')}: {msg.get('text', '')[:100]}...")
                    
                    if callback_func:
                        callback_func(msg)
                
                # Обновляем timestamp
                if new_messages:
                    last_timestamp = max(msg.get('timestamp', '') for msg in new_messages)
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

# Функции-хелперы для быстрого использования

def quick_reply(text: str):
    """Быстрый ответ в Telegram"""
    return send_to_telegram(f"💬 {text}")

def quick_status():
    """Быстрый статус системы"""
    return send_to_telegram("📊 *Статус Cursor AI*\n\n✅ Система активна\n⏰ " + datetime.now().strftime("%H:%M:%S"))

def quick_notification(text: str):
    """Быстрое уведомление"""
    return send_to_telegram(f"🔔 *Уведомление*\n\n{text}", "notification")

def list_recent_messages(count: int = 5):
    """Показать последние сообщения"""
    messages = get_user_messages(count)
    
    if not messages:
        print("📭 No messages found")
        return
    
    print(f"📬 Last {len(messages)} message(s):")
    for i, msg in enumerate(messages, 1):
        timestamp = msg.get('timestamp', '')[:19].replace('T', ' ')
        username = msg.get('username', 'Unknown')
        text = msg.get('text', '')[:100]
        print(f"{i}. [{timestamp}] {username}: {text}...")

def test_integration():
    """Тест интеграции"""
    print("🧪 Testing Cursor ↔ Telegram integration...")
    
    # Проверяем структуру
    ensure_data_dir()
    print("✅ Data directory structure OK")
    
    # Проверяем файлы
    status = show_conversation_status()
    print(f"✅ Status: {status['total_user_messages']} user messages, {status['total_cursor_commands']} cursor commands")
    
    # Тестовое сообщение
    test_result = send_to_telegram("🧪 **Тест интеграции Cursor**\n\nЭто тестовое сообщение от Cursor AI")
    if test_result:
        print("✅ Test message sent successfully")
    else:
        print("❌ Test message failed")
    
    return test_result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔧 Available commands:")
        print("  python cursor_simple_integration.py test          - Test integration")
        print("  python cursor_simple_integration.py status        - Show status")
        print("  python cursor_simple_integration.py messages      - Show recent messages")
        print("  python cursor_simple_integration.py send 'text'   - Send message")
        print("  python cursor_simple_integration.py monitor       - Start monitor")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        test_integration()
    elif command == "status":
        status = show_conversation_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif command == "messages":
        list_recent_messages()
    elif command == "send" and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        send_to_telegram(text)
    elif command == "monitor":
        start_conversation_monitor()
    else:
        print(f"❌ Unknown command: {command}") 