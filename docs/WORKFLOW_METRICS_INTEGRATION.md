# 📊 LLMStruct Workflow Metrics Integration

## Обзор

Система объективных метрик интегрирована в workflow LLMStruct для отслеживания:
- 💰 Расход и overhead токенов
- 🛤️ Количество ложных путей при выполнении master-plans
- ⚠️ Проблемы, которых можно было бы избежать  
- 📈 Эффективность выполнения задач
- 🔄 Workflow события

## 🔧 Компоненты системы

### 1. Metrics Tracker (`src/llmstruct/metrics_tracker.py`)
Центральная система отслеживания метрик:

```python
from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event

# Отслеживание токенов
track_token_usage("anthropic", "claude-3", 150, 85, 0.012)

# Отслеживание задач
track_task_start("mp002_phase1", "master_plan")
track_task_complete("mp002_phase1", "success")

# Ложные пути
track_false_path("mp002_phase1", "Tried to use old API structure")

# Workflow события
track_workflow_event("struct_json_used")
track_workflow_event("venv_activation")
```

### 2. CLI интеграция
Команды для работы с метриками:

```bash
# Статус текущей сессии
python -m llmstruct.cli metrics status

# Детальная сводка
python -m llmstruct.cli metrics summary

# Аналитические данные для графиков
python -m llmstruct.cli metrics analytics --output analytics.json --format csv

# Комплексный отчет
python -m llmstruct.cli metrics report --sessions 20 --output report.md
```

### 3. API интеграция (`test_api_simple.py`)
Упрощенный API с метриками:

```bash
# Запуск API
python test_api_simple.py

# Endpoints:
# GET /api/v1/system/health
# GET /api/v1/system/status  
# GET /api/v1/metrics
# POST /api/v1/chat/message
# POST /api/v1/cli/execute
```

### 4. Telegram Bot (`integrations/telegram_bot/simple_bot.py`)
Бот с интеграцией метрик:

```bash
export TELEGRAM_BOT_TOKEN='your_token'
cd integrations/telegram_bot
python simple_bot.py

# Команды бота:
# /status - Статус системы
# /metrics - Метрики сессии
# /struct - Состояние struct.json
# /parse - Обновить struct.json
```

## 📊 Типы метрик

### Token Usage Metrics
```python
@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int  
    total_tokens: int
    cost_estimate: float
    provider: str  # "anthropic", "openai", "mock_api"
    model: str     # "claude-3", "gpt-4", "echo_model"
    timestamp: str
```

### Task Execution Metrics
```python
@dataclass
class TaskExecution:
    task_id: str
    task_type: str        # "master_plan", "epic", "session", "command"
    started_at: str
    completed_at: str
    duration_seconds: float
    status: str          # "success", "failed", "cancelled"
    error_message: str
    false_paths: List[str]  # Описания ложных путей
    rollbacks: int       # Количество откатов
    retries: int         # Количество повторов
```

### Workflow Metrics
```python
@dataclass
class WorkflowMetrics:
    struct_json_usage: int      # Использование struct.json
    context_switches: int       # Переключения контекста
    venv_activations: int       # Активации venv
    cli_commands_executed: int  # Выполненные CLI команды
    api_calls: int             # Вызовы API
    file_operations: int       # Файловые операции
    avoidable_errors: List[str] # Избежимые ошибки
    efficiency_score: float    # Оценка эффективности (0.0-1.0)
```

## 🎯 Интеграция в workflow

### 1. Использование актуального struct.json

Система автоматически отслеживает состояние `struct.json`:

```python
# В auto_init_ai_system.py
def get_workflow_status():
    # Проверка актуальности struct.json
    struct_file = Path("struct.json")
    if struct_file.exists():
        age_hours = (time.time() - struct_file.stat().st_mtime) / 3600
        
        if age_hours < 1:
            struct_status = "fresh"
            track_workflow_event("struct_json_used")
        elif age_hours > 6:
            struct_status = "outdated"
            track_workflow_event("avoidable_error", "Using outdated struct.json")
```

### 2. Автоматическое отслеживание событий

Ключевые workflow события отслеживаются автоматически:

- `struct_json_used` - Использование struct.json
- `context_switch` - Переключение режимов контекста
- `venv_activation` - Активация виртуального окружения
- `cli_command` - Выполнение CLI команд
- `api_call` - Вызовы API
- `avoidable_error` - Ошибки, которых можно было избежать

### 3. Эффективность и рекомендации

Система рассчитывает оценку эффективности:

```python
def calculate_efficiency_score(self) -> float:
    success_rate = len(completed_tasks) / len(total_tasks)
    
    # Штрафы за неэффективность
    false_path_penalty = min(total_false_paths * 0.1, 0.5)
    rollback_penalty = min(total_rollbacks * 0.15, 0.3)
    retry_penalty = min(total_retries * 0.05, 0.2)
    
    return max(0.0, success_rate - false_path_penalty - rollback_penalty - retry_penalty)
```

## 📈 Данные для графиков

Система предоставляет данные для построения графиков:

```json
{
  "token_usage_over_time": [
    {"session": "abc123", "tokens": 1500}
  ],
  "efficiency_trends": [
    {"session": "abc123", "efficiency": 0.85}
  ],
  "error_patterns": [
    {"session": "abc123", "false_paths": 2, "rollbacks": 1}
  ],
  "cost_analysis": [
    {"session": "abc123", "cost": 0.024}
  ],
  "task_completion_rates": [
    {"session": "abc123", "completion_rate": 0.9}
  ]
}
```

## 🔧 Использование в командах

### Команды CLI с автоматическими метриками:

```bash
# Обновление struct.json (отслеживается автоматически)
python -m llmstruct.cli parse . -o struct.json

# API команды (отслеживают вызовы)
python -m llmstruct.cli api start
python -m llmstruct.cli api status

# Бот команды (отслеживают активность)
python -m llmstruct.cli bot start --type simple
```

### Workflow статус с метриками:

```bash
# Расширенный статус workflow
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"
```

Выводит:
```
🎭 WORKFLOW STATUS REPORT (Session: be348bb7)
=============================================

📅 Session: SES-001
🎯 Epic: None
🎭 Mode: ['discuss', 'meta', 'planning']
🌿 Branch: feature/personal-files-collection-20250530

📊 SESSION METRICS:
- Duration: 245s
- Efficiency Score: 0.85
- Total Tokens: 1,250
- Tasks: 8/10
- False Paths: 1

📁 STRUCT.JSON STATUS: FRESH
- Hash: ddfa9f98
- Usage Count: 3
```

## 🚀 Рекомендации по использованию

### 1. Ежедневный workflow:
```bash
# Утром - проверка статуса
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"

# В процессе работы - обновление struct.json при необходимости
python -m llmstruct.cli parse . -o struct.json

# Вечером - анализ метрик
python -m llmstruct.cli metrics summary
```

### 2. Еженедельный анализ:
```bash
# Генерация отчета за неделю
python -m llmstruct.cli metrics report --sessions 50 --output weekly_report.md

# Экспорт данных для графиков
python -m llmstruct.cli metrics analytics --output weekly_data.csv --format csv
```

### 3. Оптимизация workflow:
- Следите за efficiency_score - цель >0.8
- Минимизируйте false_paths через лучшее планирование
- Используйте актуальный struct.json (статус "fresh")
- Отслеживайте избежимые ошибки для улучшения процессов

## 📂 Файлы и директории

```
.metrics/                           # Директория метрик
├── session_YYYYMMDD_HHMMSS.json   # Данные сессий
├── aggregate_metrics.json         # Агрегированные данные
└── ...

src/llmstruct/
├── metrics_tracker.py             # Основная система метрик
├── cli.py                         # CLI интеграция (команды metrics)
└── ...

integrations/telegram_bot/
├── simple_bot.py                  # Telegram бот с метриками
└── ...

test_api_simple.py                 # API с интеграцией метрик
auto_init_ai_system.py            # Workflow статус с метриками
```

## 🎯 Следующие шаги

1. **Настройка графиков** - Использование CSV данных для визуализации
2. **Алерты** - Уведомления при низкой эффективности 
3. **Автооптимизация** - Автоматические рекомендации по улучшению
4. **Интеграция с MP-002** - Специфичные метрики для master-plan execution
5. **Расширенный анализ** - Machine learning для предсказания проблем

---

Система метрик полностью интегрирована в workflow и готова к использованию! 🚀 