#!/usr/bin/env python3
"""
🎯 Cursor Integration for Telegram Master Controller
Простые функции для интеграции Cursor с Telegram контроллером
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class CursorTelegramIntegration:
    """Интеграция Cursor с Telegram Master Controller"""
    
    def __init__(self):
        self.commands_file = Path("data/telegram/cursor_commands.json")
        self.responses_file = Path("data/telegram/cursor_responses.json")
        self.status_file = Path("data/telegram/master_status.json")
        
        # Ensure directories exist
        self.commands_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Keep track of processed commands
        self.processed_commands = set()
    
    def check_for_commands(self) -> List[Dict]:
        """Проверить новые команды от пользователя"""
        try:
            if not self.commands_file.exists():
                return []
            
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                commands = json.load(f)
            
            # Filter new commands
            new_commands = []
            for cmd in commands:
                cmd_id = cmd.get('id')
                if cmd_id and cmd_id not in self.processed_commands:
                    new_commands.append(cmd)
                    self.processed_commands.add(cmd_id)
            
            return new_commands
            
        except Exception as e:
            print(f"❌ Error checking commands: {e}")
            return []
    
    def send_response(self, message: str, response_type: str = "info"):
        """Отправить ответ пользователю в Telegram"""
        try:
            responses = []
            if self.responses_file.exists():
                with open(self.responses_file, 'r', encoding='utf-8') as f:
                    responses = json.load(f)
            
            response = {
                "id": f"resp_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "type": response_type,
                "sent": False
            }
            
            responses.append(response)
            
            # Keep only last 50 responses
            if len(responses) > 50:
                responses = responses[-50:]
            
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)
            
            print(f"📤 Response queued: {message[:50]}...")
            
        except Exception as e:
            print(f"❌ Error sending response: {e}")
    
    def update_status(self, message: str, status: str):
        """Обновить статус выполнения"""
        try:
            status_data = {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "updated_by": "cursor"
            }
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            
            print(f"📊 Status updated: {status} - {message}")
            
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def send_progress_update(self, step: str, details: str, progress: int = 0):
        """Отправить обновление прогресса"""
        message = f"""📊 **Прогресс выполнения**

🎯 **Текущий шаг:** {step}
📝 **Детали:** {details}
⏳ **Прогресс:** {progress}%

⚡ Продолжаю выполнение..."""
        
        self.send_response(message, "progress")
        self.update_status(f"{step}: {details}", "executing")
    
    def send_completion(self, summary: str, success: bool = True):
        """Отправить уведомление о завершении"""
        status_emoji = "✅" if success else "❌"
        status_text = "Завершено успешно" if success else "Завершено с ошибкой"
        
        message = f"""{status_emoji} **{status_text}**

📋 **Итоги:**
{summary}

🎯 Готов к новым командам."""
        
        self.send_response(message, "completion")
        self.update_status(status_text, "completed" if success else "failed")
    
    def ask_for_confirmation(self, question: str, context: str = ""):
        """Запросить подтверждение у пользователя"""
        message = f"""❓ **Требуется подтверждение**

📝 **Вопрос:** {question}

{f"📋 **Контекст:** {context}" if context else ""}

💬 Ответь *да* или *нет* для продолжения."""
        
        self.send_response(message, "question")
        self.update_status("Ожидание подтверждения", "waiting_confirmation")

# Convenient functions for direct use
_integration = CursorTelegramIntegration()

def check_telegram_commands() -> List[Dict]:
    """Простая функция для проверки команд"""
    return _integration.check_for_commands()

def send_telegram_message(message: str, msg_type: str = "info"):
    """Простая функция для отправки сообщений"""
    _integration.send_response(message, msg_type)

def update_telegram_status(message: str, status: str):
    """Простая функция для обновления статуса"""
    _integration.update_status(message, status)

def send_progress(step: str, details: str, progress: int = 0):
    """Простая функция для отправки прогресса"""
    _integration.send_progress_update(step, details, progress)

def send_completion(summary: str, success: bool = True):
    """Простая функция для уведомления о завершении"""
    _integration.send_completion(summary, success)

def ask_confirmation(question: str, context: str = ""):
    """Простая функция для запроса подтверждения"""
    _integration.ask_for_confirmation(question, context)

# Example usage for Cursor AI
if __name__ == "__main__":
    print("🧪 Testing Cursor Integration...")
    
    # Check for commands
    commands = check_telegram_commands()
    print(f"📥 Found {len(commands)} new commands")
    
    for cmd in commands:
        print(f"🎯 Command: {cmd.get('command')} - {cmd.get('message', '')}")
        
        if cmd.get('command') == 'start_master_plan':
            send_telegram_message("🚀 **Мастер-план запущен!**\n\n⚙️ Начинаю выполнение...")
            send_progress("Инициализация", "Подготовка системы", 10)
            
        elif cmd.get('command') == 'user_message':
            user_message = cmd.get('message', '')
            send_telegram_message(f"💬 **Получено сообщение:** {user_message}\n\n⚙️ Обрабатываю...")
    
    print("✅ Integration test completed") 