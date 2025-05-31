#!/usr/bin/env python3
"""
LLMStruct Metrics Tracker - Система объективных метрик проекта
Отслеживает токены, performance, ошибки, ложные пути при выполнении master-plans
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class TokenUsage:
    """Метрики использования токенов"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_estimate: float = 0.0
    provider: str = ""
    model: str = ""
    timestamp: str = ""

@dataclass
class TaskExecution:
    """Метрики выполнения задачи"""
    task_id: str
    task_type: str  # master_plan, epic, session, command
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    status: str = "in_progress"  # success, failed, cancelled
    error_message: Optional[str] = None
    false_paths: List[str] = None
    rollbacks: int = 0
    retries: int = 0
    
    def __post_init__(self):
        if self.false_paths is None:
            self.false_paths = []

@dataclass
class WorkflowMetrics:
    """Метрики workflow"""
    struct_json_usage: int = 0
    struct_json_last_updated: str = ""
    context_switches: int = 0
    venv_activations: int = 0
    cli_commands_executed: int = 0
    api_calls: int = 0
    file_operations: int = 0
    avoidable_errors: List[str] = None
    efficiency_score: float = 0.0
    
    def __post_init__(self):
        if self.avoidable_errors is None:
            self.avoidable_errors = []

class MetricsTracker:
    """Центральная система отслеживания метрик"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics_dir = self.project_root / ".metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        
        self.session_file = self.metrics_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.aggregate_file = self.metrics_dir / "aggregate_metrics.json"
        
        # Текущая сессия
        self.session_data = {
            "session_id": self._generate_session_id(),
            "started_at": datetime.now().isoformat(),
            "token_usage": [],
            "task_executions": [],
            "workflow_metrics": asdict(WorkflowMetrics()),
            "metadata": {
                "branch": self._get_current_branch(),
                "commit_hash": self._get_commit_hash(),
                "struct_json_hash": self._get_struct_json_hash()
            }
        }
        
        logging.info(f"📊 Metrics tracker initialized for session {self.session_data['session_id']}")
    
    def _generate_session_id(self) -> str:
        """Генерирует уникальный ID сессии"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def _get_current_branch(self) -> str:
        """Получает текущую git ветку"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_commit_hash(self) -> str:
        """Получает текущий commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_struct_json_hash(self) -> str:
        """Получает hash struct.json для отслеживания изменений"""
        struct_file = self.project_root / "struct.json"
        if struct_file.exists():
            with open(struct_file, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()[:8]
        return "missing"
    
    def track_token_usage(self, provider: str, model: str, input_tokens: int, 
                         output_tokens: int, cost_estimate: float = 0.0):
        """Отслеживание использования токенов"""
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_estimate=cost_estimate,
            provider=provider,
            model=model,
            timestamp=datetime.now().isoformat()
        )
        
        self.session_data["token_usage"].append(asdict(usage))
        logging.info(f"📊 Token usage tracked: {input_tokens}+{output_tokens}={usage.total_tokens} tokens")
        
        return usage
    
    def start_task(self, task_id: str, task_type: str) -> TaskExecution:
        """Начало выполнения задачи"""
        task = TaskExecution(
            task_id=task_id,
            task_type=task_type,
            started_at=datetime.now().isoformat()
        )
        
        self.session_data["task_executions"].append(asdict(task))
        logging.info(f"📊 Task started: {task_id} ({task_type})")
        
        return task
    
    def complete_task(self, task_id: str, status: str = "success", 
                     error_message: Optional[str] = None):
        """Завершение задачи"""
        for task_data in self.session_data["task_executions"]:
            if task_data["task_id"] == task_id:
                task_data["completed_at"] = datetime.now().isoformat()
                task_data["status"] = status
                
                if task_data["started_at"]:
                    start_time = datetime.fromisoformat(task_data["started_at"])
                    duration = (datetime.now() - start_time).total_seconds()
                    task_data["duration_seconds"] = duration
                
                if error_message:
                    task_data["error_message"] = error_message
                
                logging.info(f"📊 Task completed: {task_id} ({status}) in {task_data.get('duration_seconds', 0):.1f}s")
                break
    
    def track_false_path(self, task_id: str, false_path_description: str):
        """Отслеживание ложных путей"""
        for task_data in self.session_data["task_executions"]:
            if task_data["task_id"] == task_id:
                task_data["false_paths"].append({
                    "description": false_path_description,
                    "timestamp": datetime.now().isoformat()
                })
                logging.warning(f"📊 False path tracked for {task_id}: {false_path_description}")
                break
    
    def track_rollback(self, task_id: str):
        """Отслеживание откатов"""
        for task_data in self.session_data["task_executions"]:
            if task_data["task_id"] == task_id:
                task_data["rollbacks"] += 1
                logging.warning(f"📊 Rollback tracked for {task_id} (total: {task_data['rollbacks']})")
                break
    
    def track_retry(self, task_id: str):
        """Отслеживание повторных попыток"""
        for task_data in self.session_data["task_executions"]:
            if task_data["task_id"] == task_id:
                task_data["retries"] += 1
                logging.info(f"📊 Retry tracked for {task_id} (total: {task_data['retries']})")
                break
    
    def track_workflow_event(self, event_type: str, details: Optional[str] = None):
        """Отслеживание workflow событий"""
        workflow = self.session_data["workflow_metrics"]
        
        if event_type == "struct_json_used":
            workflow["struct_json_usage"] += 1
            workflow["struct_json_last_updated"] = datetime.now().isoformat()
        elif event_type == "context_switch":
            workflow["context_switches"] += 1
        elif event_type == "venv_activation":
            workflow["venv_activations"] += 1
        elif event_type == "cli_command":
            workflow["cli_commands_executed"] += 1
        elif event_type == "api_call":
            workflow["api_calls"] += 1
        elif event_type == "file_operation":
            workflow["file_operations"] += 1
        elif event_type == "avoidable_error" and details:
            workflow["avoidable_errors"].append({
                "error": details,
                "timestamp": datetime.now().isoformat()
            })
        
        logging.info(f"📊 Workflow event: {event_type}")
    
    def calculate_efficiency_score(self) -> float:
        """Расчет оценки эффективности"""
        tasks = self.session_data["task_executions"]
        if not tasks:
            return 0.0
        
        completed_tasks = [t for t in tasks if t["status"] == "success"]
        failed_tasks = [t for t in tasks if t["status"] == "failed"]
        
        total_false_paths = sum(len(t.get("false_paths", [])) for t in tasks)
        total_rollbacks = sum(t.get("rollbacks", 0) for t in tasks)
        total_retries = sum(t.get("retries", 0) for t in tasks)
        
        # Базовый score - процент успешных задач
        success_rate = len(completed_tasks) / len(tasks) if tasks else 0
        
        # Штрафы за неэффективность
        false_path_penalty = min(total_false_paths * 0.1, 0.5)
        rollback_penalty = min(total_rollbacks * 0.15, 0.3)
        retry_penalty = min(total_retries * 0.05, 0.2)
        
        # Итоговый score
        efficiency = max(0.0, success_rate - false_path_penalty - rollback_penalty - retry_penalty)
        
        self.session_data["workflow_metrics"]["efficiency_score"] = efficiency
        return efficiency
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Получение сводки по текущей сессии"""
        self.calculate_efficiency_score()
        
        total_tokens = sum(usage["total_tokens"] for usage in self.session_data["token_usage"])
        total_cost = sum(usage.get("cost_estimate", 0) for usage in self.session_data["token_usage"])
        
        tasks = self.session_data["task_executions"]
        completed_tasks = [t for t in tasks if t["status"] == "success"]
        
        return {
            "session_id": self.session_data["session_id"],
            "duration": self._get_session_duration(),
            "total_tokens": total_tokens,
            "estimated_cost": total_cost,
            "tasks_completed": len(completed_tasks),
            "tasks_total": len(tasks),
            "efficiency_score": self.session_data["workflow_metrics"]["efficiency_score"],
            "false_paths": sum(len(t.get("false_paths", [])) for t in tasks),
            "rollbacks": sum(t.get("rollbacks", 0) for t in tasks),
            "retries": sum(t.get("retries", 0) for t in tasks),
            "avoidable_errors": len(self.session_data["workflow_metrics"]["avoidable_errors"])
        }
    
    def _get_session_duration(self) -> float:
        """Получение длительности сессии в секундах"""
        start_time = datetime.fromisoformat(self.session_data["started_at"])
        return (datetime.now() - start_time).total_seconds()
    
    def save_session(self):
        """Сохранение данных сессии"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        # Обновление агрегированных метрик
        self._update_aggregate_metrics()
        
        logging.info(f"📊 Session metrics saved to {self.session_file}")
    
    def _update_aggregate_metrics(self):
        """Обновление агрегированных метрик"""
        if self.aggregate_file.exists():
            with open(self.aggregate_file, 'r', encoding='utf-8') as f:
                aggregate = json.load(f)
        else:
            aggregate = {
                "total_sessions": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "total_tasks": 0,
                "average_efficiency": 0.0,
                "sessions": []
            }
        
        # Добавление данных текущей сессии
        summary = self.get_session_summary()
        aggregate["sessions"].append(summary)
        aggregate["total_sessions"] += 1
        aggregate["total_tokens"] += summary["total_tokens"]
        aggregate["total_cost"] += summary["estimated_cost"]
        aggregate["total_tasks"] += summary["tasks_total"]
        
        # Пересчет средней эффективности
        efficiency_scores = [s["efficiency_score"] for s in aggregate["sessions"]]
        aggregate["average_efficiency"] = sum(efficiency_scores) / len(efficiency_scores)
        
        with open(self.aggregate_file, 'w', encoding='utf-8') as f:
            json.dump(aggregate, f, indent=2, ensure_ascii=False)
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Получение данных для построения графиков"""
        if not self.aggregate_file.exists():
            return {"error": "No aggregate data available"}
        
        with open(self.aggregate_file, 'r', encoding='utf-8') as f:
            aggregate = json.load(f)
        
        # Подготовка данных для графиков
        sessions = aggregate["sessions"]
        
        return {
            "token_usage_over_time": [
                {"session": s["session_id"], "tokens": s["total_tokens"]} 
                for s in sessions
            ],
            "efficiency_trends": [
                {"session": s["session_id"], "efficiency": s["efficiency_score"]} 
                for s in sessions
            ],
            "error_patterns": [
                {"session": s["session_id"], "false_paths": s["false_paths"], 
                 "rollbacks": s["rollbacks"], "avoidable_errors": s["avoidable_errors"]} 
                for s in sessions
            ],
            "cost_analysis": [
                {"session": s["session_id"], "cost": s["estimated_cost"]} 
                for s in sessions
            ],
            "task_completion_rates": [
                {"session": s["session_id"], 
                 "completion_rate": s["tasks_completed"] / max(s["tasks_total"], 1)} 
                for s in sessions
            ]
        }


# Глобальный экземпляр для использования в workflow
_global_tracker: Optional[MetricsTracker] = None

def get_metrics_tracker() -> MetricsTracker:
    """Получение глобального экземпляра MetricsTracker"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MetricsTracker()
    return _global_tracker

def track_token_usage(provider: str, model: str, input_tokens: int, output_tokens: int, cost: float = 0.0):
    """Удобная функция для отслеживания токенов"""
    return get_metrics_tracker().track_token_usage(provider, model, input_tokens, output_tokens, cost)

def track_task_start(task_id: str, task_type: str = "general"):
    """Удобная функция для начала отслеживания задачи"""
    return get_metrics_tracker().start_task(task_id, task_type)

def track_task_complete(task_id: str, status: str = "success", error: Optional[str] = None):
    """Удобная функция для завершения отслеживания задачи"""
    return get_metrics_tracker().complete_task(task_id, status, error)

def track_false_path(task_id: str, description: str):
    """Удобная функция для отслеживания ложных путей"""
    return get_metrics_tracker().track_false_path(task_id, description)

def track_workflow_event(event_type: str, details: Optional[str] = None):
    """Удобная функция для отслеживания workflow событий"""
    return get_metrics_tracker().track_workflow_event(event_type, details)

def track_telegram_interaction(user_message: str, bot_response: str, context_size: int = 0):
    """Отслеживание взаимодействия через Telegram с полным контекстом"""
    try:
        tracker = get_metrics_tracker()
        
        # Примерный подсчет токенов (1 токен ≈ 4 символа для русского)
        user_tokens = len(user_message) // 3  # Более точно для русского
        bot_tokens = len(bot_response) // 3
        total_tokens = user_tokens + bot_tokens + context_size
        
        interaction_data = {
            'timestamp': datetime.now().isoformat(),
            'user_message_length': len(user_message),
            'user_tokens_estimate': user_tokens,
            'bot_response_length': len(bot_response),
            'bot_tokens_estimate': bot_tokens,
            'context_tokens': context_size,
            'total_tokens_estimate': total_tokens,
            'cost_estimate_usd': total_tokens * 0.000001  # Примерная стоимость
        }
        
        if 'telegram_interactions' not in tracker.session_data:
            tracker.session_data['telegram_interactions'] = []
        
        tracker.session_data['telegram_interactions'].append(interaction_data)
        tracker.session_data['total_telegram_tokens'] = tracker.session_data.get('total_telegram_tokens', 0) + total_tokens
        
        logger.info(f"📱 Telegram interaction: {user_tokens}+{bot_tokens}+{context_size}={total_tokens} tokens")
        
    except Exception as e:
        logger.error(f"Failed to track telegram interaction: {e}")

def track_api_interaction(endpoint: str, request_tokens: int, response_tokens: int, context_tokens: int = 0):
    """Отслеживание API взаимодействия с полным контекстом"""
    try:
        tracker = get_metrics_tracker()
        
        total_tokens = request_tokens + response_tokens + context_tokens
        
        interaction_data = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'request_tokens': request_tokens,
            'response_tokens': response_tokens,
            'context_tokens': context_tokens,
            'total_tokens': total_tokens,
            'cost_estimate_usd': total_tokens * 0.000001
        }
        
        if 'api_interactions' not in tracker.session_data:
            tracker.session_data['api_interactions'] = []
            
        tracker.session_data['api_interactions'].append(interaction_data)
        tracker.session_data['total_api_tokens'] = tracker.session_data.get('total_api_tokens', 0) + total_tokens
        
        logger.info(f"🔌 API interaction: {request_tokens}+{response_tokens}+{context_tokens}={total_tokens} tokens")
        
    except Exception as e:
        logger.error(f"Failed to track API interaction: {e}")

def get_token_summary():
    """Получить сводку по токенам"""
    try:
        tracker = get_metrics_tracker()
        
        telegram_tokens = tracker.session_data.get('total_telegram_tokens', 0)
        api_tokens = tracker.session_data.get('total_api_tokens', 0)
        total_tokens = telegram_tokens + api_tokens
        
        return {
            'telegram_tokens': telegram_tokens,
            'api_tokens': api_tokens,
            'total_tokens': total_tokens,
            'estimated_cost_usd': total_tokens * 0.000001,
            'telegram_interactions_count': len(tracker.session_data.get('telegram_interactions', [])),
            'api_interactions_count': len(tracker.session_data.get('api_interactions', []))
        }
    except Exception as e:
        logger.error(f"Failed to get token summary: {e}")
        return {} 