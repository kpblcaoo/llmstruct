#!/usr/bin/env python3
"""
Cursor Telegram Reader - Читает сообщения из Telegram бота для Cursor
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TelegramLogReader:
    """Читатель логов Telegram для Cursor"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logs_dir = self.project_root / "logs" / "telegram"
        self.messages_log = self.logs_dir / "user_messages.log"
        self.cursor_commands = self.logs_dir / "cursor_commands.log"
        
    def get_latest_messages(self, count: int = 10) -> List[Dict]:
        """Получить последние сообщения"""
        if not self.messages_log.exists():
            return []
        
        try:
            with open(self.messages_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбираем записи
            entries = content.split('===')[1:]  # Пропускаем первый пустой элемент
            messages = []
            
            for entry in entries[-count:]:
                if entry.strip():
                    lines = entry.strip().split('\n')
                    if len(lines) >= 4:
                        timestamp_line = lines[0].strip()
                        user_line = lines[1].strip()
                        type_line = lines[2].strip()
                        message_line = lines[3].strip()
                        
                        message_data = {
                            'timestamp': timestamp_line,
                            'user': user_line.replace('👤 USER:', '').strip(),
                            'type': type_line.replace('📱 TYPE:', '').strip(),
                            'message': message_line.replace('💬 MESSAGE:', '').strip()
                        }
                        messages.append(message_data)
            
            return messages
            
        except Exception as e:
            print(f"❌ Ошибка чтения сообщений: {e}")
            return []
    
    def get_cursor_commands(self, hours: int = 24) -> List[Dict]:
        """Получить команды для Cursor за последние часы"""
        if not self.cursor_commands.exists():
            return []
        
        try:
            with open(self.cursor_commands, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            commands = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for line in lines:
                if '| CURSOR COMMAND:' in line:
                    parts = line.split('| CURSOR COMMAND:', 1)
                    if len(parts) == 2:
                        timestamp_str = parts[0].strip()
                        command = parts[1].strip()
                        
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            if timestamp >= cutoff_time:
                                commands.append({
                                    'timestamp': timestamp_str,
                                    'command': command
                                })
                        except ValueError:
                            continue
            
            return commands
            
        except Exception as e:
            print(f"❌ Ошибка чтения команд Cursor: {e}")
            return []
    
    def watch_new_messages(self, callback=None):
        """Мониторинг новых сообщений в реальном времени"""
        if not self.messages_log.exists():
            print("📄 Файл логов еще не создан. Ожидание...")
            return
        
        print(f"👀 Мониторинг новых сообщений в {self.messages_log}")
        print("Нажмите Ctrl+C для остановки")
        
        # Получаем текущий размер файла
        last_size = self.messages_log.stat().st_size
        
        try:
            while True:
                current_size = self.messages_log.stat().st_size
                
                if current_size > last_size:
                    # Читаем новый контент
                    with open(self.messages_log, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_content = f.read()
                    
                    if new_content.strip():
                        print(f"\n🆕 Новое сообщение:")
                        print(new_content)
                        
                        if callback:
                            callback(new_content)
                    
                    last_size = current_size
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Мониторинг остановлен")
    
    def print_status(self):
        """Показать статус логирования"""
        print("📊 Статус Telegram логирования:")
        print(f"📁 Папка логов: {self.logs_dir}")
        print(f"📄 Сообщения: {self.messages_log}")
        print(f"🎯 Команды Cursor: {self.cursor_commands}")
        
        # Проверяем существование файлов
        messages_exist = self.messages_log.exists()
        commands_exist = self.cursor_commands.exists()
        
        print(f"✅ Файл сообщений: {'Существует' if messages_exist else 'Не создан'}")
        print(f"✅ Файл команд: {'Существует' if commands_exist else 'Не создан'}")
        
        if messages_exist:
            stat = self.messages_log.stat()
            print(f"📏 Размер сообщений: {stat.st_size} байт")
            print(f"⏰ Последнее изменение: {datetime.fromtimestamp(stat.st_mtime)}")
        
        if commands_exist:
            stat = self.cursor_commands.stat()
            print(f"📏 Размер команд: {stat.st_size} байт")
            print(f"⏰ Последнее изменение: {datetime.fromtimestamp(stat.st_mtime)}")

def main():
    """Главная функция"""
    import sys
    
    reader = TelegramLogReader()
    
    if len(sys.argv) < 2:
        print("🤖 Cursor Telegram Reader")
        print("Использование:")
        print("  python cursor_telegram_reader.py status    - показать статус")
        print("  python cursor_telegram_reader.py latest    - последние сообщения")
        print("  python cursor_telegram_reader.py commands  - команды для Cursor")
        print("  python cursor_telegram_reader.py watch     - мониторинг в реальном времени")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        reader.print_status()
        
    elif command == "latest":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        messages = reader.get_latest_messages(count)
        
        if messages:
            print(f"📱 Последние {len(messages)} сообщений:")
            for msg in messages:
                print(f"\n{msg['timestamp']}")
                print(f"👤 {msg['user']}")
                print(f"💬 {msg['message']}")
                print("-" * 50)
        else:
            print("📭 Сообщений пока нет")
    
    elif command == "commands":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        commands = reader.get_cursor_commands(hours)
        
        if commands:
            print(f"🎯 Команды для Cursor за последние {hours} часов:")
            for cmd in commands:
                print(f"{cmd['timestamp']} | {cmd['command']}")
        else:
            print("🎯 Команд для Cursor пока нет")
    
    elif command == "watch":
        reader.watch_new_messages()
    
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 