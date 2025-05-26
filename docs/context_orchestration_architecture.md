# Smart Context Orchestration Architecture

## Проблема

У llmstruct есть два основных сценария использования LLM, которые требуют разной оптимизации контекста:

1. **Direct CLI API calls** (`llmstruct query`, `llmstruct interactive`) - нужен полный, богатый контекст
2. **VS Code Copilot integration** - нужен легковесный, фокусированный контекст для избежания превышения лимитов токенов

## Решение: Multi-Mode Context System

### 1. Контекстные режимы (Context Modes)

```python
class ContextMode(Enum):
    FULL = "full"           # Для прямых CLI вызовов
    FOCUSED = "focused"     # Для VS Code Copilot
    MINIMAL = "minimal"     # Для быстрых операций
    SESSION = "session"     # Для сессионной работы
```

### 2. Smart Context Selector

```python
class ContextSelector:
    def select_optimal_context(self, scenario: str, file_path: str = None) -> Dict[str, Any]:
        """Выбирает оптимальный контекст в зависимости от сценария"""
        
        if scenario == "cli_direct":
            return self.build_full_context()
        elif scenario == "vscode_copilot":
            return self.build_focused_context(file_path)
        elif scenario == "session_work":
            return self.build_session_context()
```

### 3. Иерархия контекста по токенам

#### Level 0: Core (< 500 tokens)
- Краткое описание проекта
- Основные цели из `init.json`
- Текущая сессия

#### Level 1: Essential (< 2000 tokens)
- Структура проекта (упрощённая)
- Активные задачи (top 5)
- Ключевые файлы для текущей работы

#### Level 2: Comprehensive (< 8000 tokens)
- Полная структура `struct.json`
- Расширенный список задач и идей
- Зависимости и архитектура

#### Level 3: Full (unlimited)
- Весь доступный контекст
- Полные метаданные
- История изменений

### 4. Context Loading Strategy

```python
class SmartContextLoader:
    def load_for_scenario(self, scenario: str, context_budget: int = None):
        """Загружает контекст с учётом бюджета токенов"""
        
        if scenario == "vscode_copilot":
            # Бюджет: 2000 токенов максимум
            return self.load_progressive_context(max_tokens=2000)
        
        elif scenario == "cli_interactive":
            # Без ограничений, полный контекст
            return self.load_full_context()
        
        elif scenario == "session_start":
            # Контекст сессии + essential
            return self.load_session_context()
```

## Преимущества

1. **Эффективность токенов**: VS Code Copilot получает только нужный контекст
2. **Богатство контекста**: CLI режим получает полную информацию
3. **Адаптивность**: Система адаптируется к доступному бюджету токенов
4. **Сессионность**: Поддержка работы с сессиями

## Интеграция с текущей системой

- Расширение существующего `CopilotContextManager`
- Добавление smart selection в CLI команды
- Интеграция с системой сессий (`ai_sessions.json`)
- Обратная совместимость с текущими 4 уровнями

## Пример использования

```bash
# Полный контекст для CLI
llmstruct interactive . --context-mode full

# Фокусированный контекст для файла
llmstruct copilot . suggest --context-mode focused --file src/main.py

# Сессионный контекст
llmstruct session start --load-context session
```
