#!/usr/bin/env python3
"""
MP-002A Progress Bot - Telegram контроль выполнения Smart Wrapper реализации
Этапная отчетность, контроль качества, интерактивное управление
"""

import asyncio
import json
import os
import sys
import httpx
from datetime import datetime
from pathlib import Path

# Добавляем путь к основному проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

class MP002ProgressBot:
    """
    Telegram бот для контроля реализации MP-002A Smart Wrapper
    """
    
    def __init__(self, token):
        self.token = token
        self.api_base = "http://localhost:8000/api/v1"
        self.project_root = Path(__file__).parent.parent.parent
        self.progress_file = self.project_root / ".personal" / "mp002_progress.json"
        
        # Фазы реализации MP-002A
        self.phases = {
            "phase_1": {
                "name": "MVP Smart Wrapper",
                "estimated_hours": "1-2 дня",
                "tasks": [
                    "Создать SmartWorkflow класс",
                    "Реализовать ContextAnalyzer с venv detection", 
                    "Интегрировать с AccessController (Boss/Team)",
                    "Базовая CLI команда smart_workflow.py",
                    "Тестирование на простых сценариях"
                ],
                "success_criteria": [
                    "100% автоактивация venv при необходимости",
                    "Различие Boss/Team команд работает",
                    "Fallback на старые команды при ошибках"
                ]
            },
            "phase_2": {
                "name": "Epic Integration", 
                "estimated_hours": "1-2 дня",
                "tasks": [
                    "Реализовать EpicAutofiller с Boss/Team разделением",
                    "Интеграция с GitHub sync (enhanced vs basic)",
                    "Шаблонная система для автозаполнения",
                    "Fallback handlers и error processing",
                    "Тестирование epic creation workflows"
                ],
                "success_criteria": [
                    "80%+ корректность автозаполнения",
                    "Правильное разделение доступа Boss/Team",
                    "Интеграция с существующими GitHub workflows"
                ]
            },
            "phase_3": {
                "name": "AI Enhancement",
                "estimated_hours": "1 день", 
                "tasks": [
                    "Hybrid правила + адаптивность в ContextAnalyzer",
                    "Machine learning для командных паттернов",
                    "Предиктивные предложения действий",
                    "Интеграция с AI self-awareness системой",
                    "Оптимизация JSON структуры для LLM"
                ],
                "success_criteria": [
                    "Субъективная оценка удобства 8/10+",
                    "Сокращение времени workflow на 50%+",
                    "Smart context switching работает корректно"
                ]
            }
        }
        
        # Инициализация прогресса
        self.init_progress_tracking()
    
    def init_progress_tracking(self):
        """Инициализация системы отслеживания прогресса"""
        if not self.progress_file.exists():
            initial_progress = {
                "started_at": datetime.now().isoformat(),
                "current_phase": "phase_1",
                "phases": {
                    phase_id: {
                        "status": "pending",
                        "started_at": None,
                        "completed_at": None,
                        "tasks_completed": [],
                        "issues": [],
                        "user_feedback": []
                    } for phase_id in self.phases.keys()
                },
                "overall_status": "in_progress",
                "blocking_issues": [],
                "user_approvals": []
            }
            
            # Создаем .personal если не существует
            self.progress_file.parent.mkdir(exist_ok=True)
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(initial_progress, f, indent=2, ensure_ascii=False)
    
    def load_progress(self):
        """Загрузка текущего прогресса"""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            self.init_progress_tracking()
            return self.load_progress()
    
    def save_progress(self, progress):
        """Сохранение прогресса"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    async def send_message(self, chat_id, text, parse_mode="Markdown"):
        """Отправка сообщения в Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                })
                return response.json()
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                return {"ok": False, "error": str(e)}
    
    async def report_phase_start(self, chat_id, phase_id):
        """Отчет о начале фазы"""
        progress = self.load_progress()
        phase = self.phases[phase_id]
        
        # Обновляем прогресс
        progress["current_phase"] = phase_id
        progress["phases"][phase_id]["status"] = "in_progress"
        progress["phases"][phase_id]["started_at"] = datetime.now().isoformat()
        self.save_progress(progress)
        
        message = f"""
🚀 **НАЧАЛАСЬ ФАЗА {phase_id.upper()}**: {phase['name']}

⏱️ **Оценка времени**: {phase['estimated_hours']}

📋 **Задачи фазы**:
"""
        
        for i, task in enumerate(phase['tasks'], 1):
            message += f"{i}. {task}\n"
        
        message += f"""
🎯 **Критерии успеха**:
"""
        
        for i, criteria in enumerate(phase['success_criteria'], 1):
            message += f"• {criteria}\n"
        
        message += f"\n💬 Начинаю работу! Буду отчитываться о прогрессе."
        
        await self.send_message(chat_id, message)
    
    async def report_task_completion(self, chat_id, phase_id, task_description, details=""):
        """Отчет о завершении задачи"""
        progress = self.load_progress()
        
        # Добавляем завершенную задачу
        progress["phases"][phase_id]["tasks_completed"].append({
            "task": task_description,
            "completed_at": datetime.now().isoformat(),
            "details": details
        })
        self.save_progress(progress)
        
        # Подсчитываем прогресс фазы
        total_tasks = len(self.phases[phase_id]['tasks'])
        completed_tasks = len(progress["phases"][phase_id]["tasks_completed"])
        percentage = (completed_tasks / total_tasks) * 100
        
        message = f"""
✅ **ЗАДАЧА ВЫПОЛНЕНА** ({completed_tasks}/{total_tasks})

**Фаза**: {self.phases[phase_id]['name']}
**Задача**: {task_description}
**Прогресс**: {percentage:.1f}%

{'📋 **Детали**: ' + details if details else ''}

{'🎉 **ФАЗА ГОТОВА К ЗАВЕРШЕНИЮ!**' if completed_tasks == total_tasks else f'⏭️ Переход к следующей задаче...'}
"""
        
        await self.send_message(chat_id, message)
        
        # Если все задачи выполнены, запрашиваем одобрение
        if completed_tasks == total_tasks:
            await self.request_phase_approval(chat_id, phase_id)
    
    async def request_phase_approval(self, chat_id, phase_id):
        """Запрос одобрения завершения фазы"""
        phase = self.phases[phase_id]
        
        message = f"""
🎯 **ФАЗА {phase_id.upper()} ЗАВЕРШЕНА**: {phase['name']}

**Критерии успеха для проверки**:
"""
        
        for i, criteria in enumerate(phase['success_criteria'], 1):
            message += f"{i}. {criteria}\n"
        
        message += f"""
❓ **Нужно ваше одобрение для перехода к следующей фазе.**

Команды:
• `/approve {phase_id}` - одобрить и перейти дальше
• `/issues {phase_id}` - сообщить о проблемах  
• `/details {phase_id}` - посмотреть детали выполнения
• `/status` - общий статус проекта
"""
        
        await self.send_message(chat_id, message)
    
    async def report_issue(self, chat_id, phase_id, issue_description):
        """Отчет о проблеме"""
        progress = self.load_progress()
        
        issue = {
            "description": issue_description,
            "reported_at": datetime.now().isoformat(),
            "phase": phase_id,
            "status": "open"
        }
        
        progress["blocking_issues"].append(issue)
        progress["phases"][phase_id]["issues"].append(issue)
        self.save_progress(progress)
        
        message = f"""
⚠️ **ПРОБЛЕМА ОБНАРУЖЕНА**

**Фаза**: {self.phases[phase_id]['name']}
**Описание**: {issue_description}

🤔 **Что делать?**
Отправьте одну из команд:
• `/solution <описание решения>` - предложить решение
• `/continue` - продолжить несмотря на проблему  
• `/stop` - остановить выполнение для анализа

Жду ваших указаний! 🙏
"""
        
        await self.send_message(chat_id, message)
    
    async def get_overall_status(self, chat_id):
        """Получение общего статуса проекта"""
        progress = self.load_progress()
        
        message = f"""
📊 **СТАТУС MP-002A SMART WRAPPER**

**Начат**: {progress['started_at'][:10]}
**Общий статус**: {progress['overall_status']}
**Текущая фаза**: {progress['current_phase']}

"""
        
        for phase_id, phase_data in progress["phases"].items():
            phase_info = self.phases[phase_id]
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄", 
                "completed": "✅",
                "blocked": "❌"
            }.get(phase_data["status"], "❓")
            
            completed_tasks = len(phase_data.get("tasks_completed", []))
            total_tasks = len(phase_info["tasks"])
            
            message += f"{status_emoji} **{phase_info['name']}**: {completed_tasks}/{total_tasks} задач\n"
        
        blocking_issues = len(progress.get("blocking_issues", []))
        if blocking_issues > 0:
            message += f"\n⚠️ **Блокирующие проблемы**: {blocking_issues}"
        
        message += f"""

**Доступные команды**:
• `/details <phase>` - детали фазы
• `/approve <phase>` - одобрить фазу
• `/issues <phase>` - сообщить о проблемах
• `/continue` - продолжить работу
• `/help` - справка по командам
"""
        
        await self.send_message(chat_id, message)
    
    async def handle_message(self, update):
        """Обработка входящих сообщений"""
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if not text:
            return
        
        # Парсинг команд
        if text.startswith("/"):
            await self.handle_command(chat_id, text)
        else:
            # Обычные сообщения интерпретируем как feedback
            await self.handle_feedback(chat_id, text)
    
    async def handle_command(self, chat_id, command):
        """Обработка команд"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "/start":
            await self.send_welcome(chat_id)
        elif cmd == "/status":
            await self.get_overall_status(chat_id)
        elif cmd == "/approve" and args:
            await self.approve_phase(chat_id, args[0])
        elif cmd == "/issues" and args:
            await self.report_user_issues(chat_id, args[0], " ".join(args[1:]))
        elif cmd == "/details" and args:
            await self.show_phase_details(chat_id, args[0])
        elif cmd == "/continue":
            await self.continue_work(chat_id)
        elif cmd == "/help":
            await self.show_help(chat_id)
        else:
            await self.send_message(chat_id, f"❓ Неизвестная команда: {cmd}\nИспользуйте /help для справки")
    
    async def send_welcome(self, chat_id):
        """Приветственное сообщение"""
        message = """
🤖 **MP-002A Progress Bot**

Я контролирую выполнение Smart Wrapper реализации!

**Мои функции**:
✅ Отчеты о прогрессе по фазам
⚠️ Уведомления о проблемах  
🎯 Запросы одобрения этапов
📊 Статистика выполнения
💬 Интерактивное управление

Используйте /status для начала! 🚀
"""
        await self.send_message(chat_id, message)
    
    async def approve_phase(self, chat_id, phase_id):
        """Одобрение фазы пользователем"""
        progress = self.load_progress()
        
        if phase_id not in self.phases:
            await self.send_message(chat_id, f"❌ Неизвестная фаза: {phase_id}")
            return
        
        # Обновляем статус
        progress["phases"][phase_id]["status"] = "completed"
        progress["phases"][phase_id]["completed_at"] = datetime.now().isoformat()
        progress["user_approvals"].append({
            "phase": phase_id,
            "approved_at": datetime.now().isoformat()
        })
        
        # Определяем следующую фазу
        phases_list = list(self.phases.keys())
        current_idx = phases_list.index(phase_id)
        
        if current_idx < len(phases_list) - 1:
            next_phase = phases_list[current_idx + 1]
            progress["current_phase"] = next_phase
        else:
            progress["overall_status"] = "completed"
        
        self.save_progress(progress)
        
        message = f"""
✅ **ФАЗА {phase_id.upper()} ОДОБРЕНА!**

{self.phases[phase_id]['name']} завершена успешно.
"""
        
        if progress["overall_status"] == "completed":
            message += "\n🎉 **ВСЕ ФАЗЫ ЗАВЕРШЕНЫ! MP-002A РЕАЛИЗОВАН!** 🎉"
        else:
            next_phase = progress["current_phase"] 
            message += f"\n⏭️ Переход к следующей фазе: {self.phases[next_phase]['name']}"
        
        await self.send_message(chat_id, message)
        
        # Автоматически начинаем следующую фазу
        if progress["overall_status"] != "completed":
            await self.report_phase_start(chat_id, progress["current_phase"])
    
    async def handle_feedback(self, chat_id, text):
        """Обработка обычных сообщений как feedback"""
        progress = self.load_progress()
        current_phase = progress.get("current_phase")
        
        if current_phase:
            progress["phases"][current_phase]["user_feedback"].append({
                "message": text,
                "timestamp": datetime.now().isoformat()
            })
            self.save_progress(progress)
        
        await self.send_message(chat_id, f"📝 Feedback записан! Спасибо за обратную связь.\n\nИспользуйте /status для просмотра прогресса.")


# Функции для интеграции с основным ботом
async def start_mp002_bot():
    """Запуск MP-002A бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен")
        print("Установите токен: export TELEGRAM_BOT_TOKEN='your_token'")
        return
    
    bot = MP002ProgressBot(token)
    
    print("🤖 MP-002A Progress Bot запущен!")
    print("📱 Доступные команды в Telegram:")
    print("   /start - начало работы")
    print("   /status - текущий статус")
    print("   /approve <phase> - одобрить фазу")
    print("   /issues <phase> - сообщить о проблемах")
    
    # Здесь должна быть интеграция с Telegram polling
    # Для демонстрации просто показываем что бот готов
    
    return bot


if __name__ == "__main__":
    asyncio.run(start_mp002_bot()) 