#!/usr/bin/env python3
"""
Dummy Work Executor - Тестирование двусторонней связи с пользователем через Telegram
"""

import os
import time
import asyncio
from datetime import datetime
from pathlib import Path

# Интеграция с метриками
try:
    import sys
    sys.path.append('.')
    from src.llmstruct.metrics_tracker import track_task_start, track_task_complete, track_workflow_event
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Telegram интеграция
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    
class DummyWorkExecutor:
    """Исполнитель dummy work с двусторонней связью"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_chat_id = -4938821563  # Из логов
        self.phase = "dummy_start"
        self.work_id = f"dummy_work_{int(time.time())}"
        
        if TELEGRAM_AVAILABLE and self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None
            
        if METRICS_AVAILABLE:
            track_workflow_event("dummy_work_start", self.work_id)
    
    async def send_message(self, message: str):
        """Отправка сообщения пользователю через Telegram"""
        if not self.bot:
            print(f"📱 [TELEGRAM SIMULATION]: {message}")
            return False
            
        try:
            await self.bot.send_message(
                chat_id=self.user_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            print(f"✅ Сообщение отправлено пользователю")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def check_user_response(self, expected_keywords: list = None) -> tuple[bool, str]:
        """Проверка ответа пользователя из логов"""
        messages_log = Path("logs/telegram/user_messages.log")
        
        if not messages_log.exists():
            return False, ""
            
        try:
            with open(messages_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем последние сообщения
            entries = content.split('===')
            if len(entries) < 2:
                return False, ""
                
            # Берем последнее сообщение
            last_entry = entries[-2]
            lines = last_entry.strip().split('\n')
            
            if len(lines) >= 5:
                message_line = next((line for line in lines if line.startswith('💬 MESSAGE:')), '')
                if message_line:
                    message = message_line.replace('💬 MESSAGE:', '').strip()
                    
                    # Если ключевые слова не указаны, возвращаем любой ответ
                    if not expected_keywords:
                        return True, message
                    
                    # Проверяем ключевые слова
                    message_lower = message.lower()
                    for keyword in expected_keywords:
                        if keyword.lower() in message_lower:
                            return True, message
                            
            return False, ""
            
        except Exception as e:
            print(f"❌ Ошибка чтения логов: {e}")
            return False, ""
    
    async def wait_for_user_input(self, timeout: int = 60, expected_keywords: list = None) -> tuple[bool, str]:
        """Ожидание ответа пользователя с таймаутом"""
        print(f"⏳ Ожидаю ответ пользователя (макс. {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            has_response, message = self.check_user_response(expected_keywords)
            if has_response:
                print(f"✅ Получен ответ: {message}")
                return True, message
            
            await asyncio.sleep(2)  # Проверяем каждые 2 секунды
            
        print(f"⏰ Таймаут ожидания ответа ({timeout}s)")
        return False, ""
    
    async def dummy_phase_1(self):
        """Dummy Phase 1: Тестирование связи"""
        print("🚀 DUMMY PHASE 1: Начинаю тестирование связи...")
        
        if METRICS_AVAILABLE:
            task_id = track_task_start(self.work_id + "_phase1", "dummy_communication_test")
        
        # Отправляем первое сообщение
        message = f"""🎯 *DUMMY WORK PHASE 1 ЗАПУЩЕНА*

🧪 *Тестирую двустороннюю связь:*
• ✅ Получил команду "Старт dummy" из Telegram
• ✅ Markdown форматирование исправлено 
• ✅ Метрики отслеживают процесс

❓ *Dummy вопрос для теста:*
Какой цвет больше нравится - синий или красный?

📝 *Отвечайте любым сообщением в чат.*
⏰ *Жду ответ 30 секунд...*"""
        
        await self.send_message(message)
        
        # Ждем ответ пользователя
        got_response, user_message = await self.wait_for_user_input(30)
        
        if got_response:
            # Отправляем подтверждение
            response_msg = f"""✅ *ОТЛИЧНО! Связь работает!*

👤 *Ваш ответ:* "{user_message}"

🎯 *Phase 1 завершена успешно!*
📊 *Переход к Phase 2...*"""
            
            await self.send_message(response_msg)
            
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "success", f"User responded: {user_message}")
            
            return True, user_message
        else:
            # Таймаут
            timeout_msg = f"""⏰ *ТАЙМАУТ Phase 1*

Не получил ответ за 30 секунд.
🔄 *Продолжаю с Phase 2...*"""
            
            await self.send_message(timeout_msg)
            
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "timeout", "No user response")
            
            return False, ""
    
    async def dummy_phase_2(self):
        """Dummy Phase 2: Готовность к мастер-плану"""
        print("🚀 DUMMY PHASE 2: Проверка готовности к мастер-плану...")
        
        if METRICS_AVAILABLE:
            task_id = track_task_start(self.work_id + "_phase2", "dummy_master_plan_readiness")
        
        message = f"""🎯 *DUMMY WORK PHASE 2*

📋 *Проверяю готовность инфраструктуры к мастер-плану:*

✅ *Система метрик:* {'Активна' if METRICS_AVAILABLE else 'Отключена'}
✅ *Telegram бот:* {'Работает' if self.bot else 'Симуляция'}
✅ *Логирование:* Активно
✅ *Двусторонняя связь:* Протестирована

🤔 *Dummy вопрос про мастер-план:*
Готовы ли вы к поэтапному выполнению мастер-плана?

💬 *Ответьте:*
• "да" / "готов" - начинаем мастер-план
• "нет" / "не готов" - остаемся в тестовом режиме 
• любое другое - продолжаем dummy работу

⏰ *Жду ответ 45 секунд...*"""
        
        await self.send_message(message)
        
        # Ждем ответ пользователя
        got_response, user_message = await self.wait_for_user_input(45, ["да", "готов", "нет", "не готов"])
        
        if got_response:
            user_lower = user_message.lower()
            
            if any(word in user_lower for word in ["да", "готов", "старт", "начин"]):
                # Пользователь готов к мастер-плану
                ready_msg = f"""🚀 *ОТЛИЧНО! ГОТОВНОСТЬ ПОДТВЕРЖДЕНА!*

👤 *Ваш ответ:* "{user_message}"

✅ *DUMMY WORK ЗАВЕРШЕНА УСПЕШНО!*

🎯 *ГОТОВ К ВЫПОЛНЕНИЮ МАСТЕР-ПЛАНА:*
• Двусторонняя связь протестирована ✅
• Метрики настроены ✅  
• Workflow интеграция активна ✅
• Система готова к поэтапной работе ✅

⏰ *Ожидаю подтверждения начала мастер-плана...*

🔄 *Команды для продолжения:*
• "начать мастер-план" 
• "создать ветку"
• "коммит изменения" """
                
                await self.send_message(ready_msg)
                
                if METRICS_AVAILABLE:
                    track_task_complete(task_id, "success", f"User ready: {user_message}")
                    track_workflow_event("dummy_work_success", "ready_for_master_plan")
                
                return "ready_for_master_plan", user_message
                
            elif any(word in user_lower for word in ["нет", "не готов", "подожди"]):
                # Пользователь не готов
                not_ready_msg = f"""⏸ *ПОНЯЛ! НЕ ГОТОВЫ ЕЩЕ*

👤 *Ваш ответ:* "{user_message}"

✅ *DUMMY WORK ЗАВЕРШЕНА!*

📝 *Остаемся в тестовом режиме.*
🔄 *Готов продолжить, когда скажете.*

💬 *Команды для работы:*
• "готов к мастер-плану"
• "тест связи"
• "статус системы" """
                
                await self.send_message(not_ready_msg)
                
                if METRICS_AVAILABLE:
                    track_task_complete(task_id, "success", f"User not ready: {user_message}")
                    track_workflow_event("dummy_work_success", "staying_in_test_mode")
                
                return "test_mode", user_message
            else:
                # Неопределенный ответ
                unclear_msg = f"""🤔 *НЕОПРЕДЕЛЕННЫЙ ОТВЕТ*

👤 *Ваш ответ:* "{user_message}"

✅ *DUMMY WORK ЗАВЕРШЕНА!*

📝 *Продолжаю dummy работу для тестирования.*
🔄 *Готов к дальнейшим командам.*"""
                
                await self.send_message(unclear_msg)
                
                if METRICS_AVAILABLE:
                    track_task_complete(task_id, "success", f"Unclear response: {user_message}")
                    track_workflow_event("dummy_work_success", "continuing_dummy")
                
                return "continue_dummy", user_message
        else:
            # Таймаут
            timeout_msg = f"""⏰ *ТАЙМАУТ Phase 2*

Не получил ответ за 45 секунд.

✅ *DUMMY WORK ЗАВЕРШЕНА!*

📝 *Система готова к работе.*
🔄 *Ожидаю дальнейших команд.*"""
            
            await self.send_message(timeout_msg)
            
            if METRICS_AVAILABLE:
                track_task_complete(task_id, "timeout", "No response to master plan readiness")
                track_workflow_event("dummy_work_complete", "timeout")
            
            return "timeout", ""
    
    async def execute_dummy_work(self):
        """Выполнение полного цикла dummy work"""
        print("🎯 НАЧИНАЮ DUMMY WORK EXECUTION")
        print("="*50)
        
        try:
            # Phase 1: Тестирование связи
            phase1_success, phase1_response = await self.dummy_phase_1()
            
            await asyncio.sleep(3)  # Пауза между фазами
            
            # Phase 2: Готовность к мастер-плану  
            phase2_result, phase2_response = await self.dummy_phase_2()
            
            # Финальный отчет
            final_msg = f"""📊 *DUMMY WORK ОТЧЕТ*

*Phase 1 (Связь):* {'✅ Успех' if phase1_success else '⏰ Таймаут'}
*Phase 2 (Готовность):* {phase2_result}

*Результат:* Готов к следующему этапу!
*Время:* {datetime.now().strftime('%H:%M:%S')}

🚀 *Система полностью готова к работе!*"""
            
            await self.send_message(final_msg)
            
            print("✅ DUMMY WORK ЗАВЕРШЕНА УСПЕШНО!")
            print(f"Результат Phase 2: {phase2_result}")
            
            return phase2_result
            
        except Exception as e:
            error_msg = f"❌ *ОШИБКА DUMMY WORK*\n\n{str(e)}"
            await self.send_message(error_msg)
            print(f"❌ Ошибка: {e}")
            
            if METRICS_AVAILABLE:
                track_workflow_event("dummy_work_error", str(e))
            
            return "error"

async def main():
    """Главная функция"""
    print("🚀 DUMMY WORK EXECUTOR")
    print("="*30)
    
    executor = DummyWorkExecutor()
    result = await executor.execute_dummy_work()
    
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ: {result}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 