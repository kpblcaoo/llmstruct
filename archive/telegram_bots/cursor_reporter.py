#!/usr/bin/env python3
"""
Cursor Task Reporter
Простая функция для отправки отчетов о задачах в Telegram
"""

import httpx
import asyncio
import os
from datetime import datetime
from typing import Optional

class CursorReporter:
    """Отправляет отчеты о задачах в Telegram"""
    
    def __init__(self, bot_token: str = None, chat_id: int = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or -4938821563  # Ваш chat_id
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN required")
    
    async def send_report(self, task: str, status: str, details: str = "", priority: str = "normal"):
        """Отправляет отчет о задаче"""
        
        # Эмодзи для статуса
        status_emojis = {
            "started": "🚀",
            "progress": "⚙️", 
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
            "cancelled": "🚫"
        }
        
        # Эмодзи для приоритета
        priority_emojis = {
            "low": "🟢",
            "normal": "🔵", 
            "high": "🟡",
            "urgent": "🔴"
        }
        
        status_emoji = status_emojis.get(status.lower(), "📋")
        priority_emoji = priority_emojis.get(priority.lower(), "🔵")
        
        # Экранируем специальные символы Markdown
        def escape_markdown(text):
            """Экранирует специальные символы Markdown"""
            escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in escape_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        # Формируем сообщение без сложного форматирования
        message = f"""{status_emoji} *Cursor Task Report*

{priority_emoji} *Priority:* {priority.title()}
📋 *Task:* {escape_markdown(task)}
📊 *Status:* {status.title()}
🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{escape_markdown(details)}

_Sent from Cursor IDE_"""
        
        # Отправляем сообщение
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data)
                result = response.json()
                
                if result.get("ok"):
                    print(f"✅ Report sent: {task} - {status}")
                    return True
                else:
                    print(f"❌ Failed to send report: {result}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error sending report: {e}")
                return False

# Простые функции для использования
async def report_task_started(task: str, details: str = ""):
    """Отчет о начале задачи"""
    reporter = CursorReporter()
    return await reporter.send_report(task, "started", details)

async def report_task_progress(task: str, details: str = ""):
    """Отчет о прогрессе задачи"""
    reporter = CursorReporter()
    return await reporter.send_report(task, "progress", details)

async def report_task_completed(task: str, details: str = ""):
    """Отчет о завершении задачи"""
    reporter = CursorReporter()
    return await reporter.send_report(task, "completed", details)

async def report_task_failed(task: str, details: str = ""):
    """Отчет об ошибке задачи"""
    reporter = CursorReporter()
    return await reporter.send_report(task, "failed", details, "high")

# Синхронные версии для удобства
def report_started(task: str, details: str = ""):
    """Синхронная версия - отчет о начале"""
    return asyncio.run(report_task_started(task, details))

def report_progress(task: str, details: str = ""):
    """Синхронная версия - отчет о прогрессе"""
    return asyncio.run(report_task_progress(task, details))

def report_completed(task: str, details: str = ""):
    """Синхронная версия - отчет о завершении"""
    return asyncio.run(report_task_completed(task, details))

def report_failed(task: str, details: str = ""):
    """Синхронная версия - отчет об ошибке"""
    return asyncio.run(report_task_failed(task, details))

# Пример использования
if __name__ == "__main__":
    # Тестовый отчет
    test_task = "Testing Cursor Reporter"
    test_details = """Проверяем работу системы отчетов:
• Отправка сообщений в Telegram
• Форматирование сообщений  
• Обработка ошибок
• Синхронные и асинхронные вызовы"""
    
    print("📋 Sending test report...")
    success = report_started(test_task, test_details)
    
    if success:
        print("✅ Test report sent successfully!")
    else:
        print("❌ Test report failed!") 