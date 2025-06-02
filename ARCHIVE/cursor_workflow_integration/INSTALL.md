# ⚡ Быстрая установка Cursor AI Integration

## 🎯 За 3 минуты

### 1. Скопировать файлы
```bash
# Перейти в папку вашего проекта
cd /path/to/your/llmstruct/project

# Скопировать основные файлы
cp cursor_workflow_integration/files/auto_init_ai_system.py .
cp cursor_workflow_integration/files/.cursorrules .

# Скопировать VS Code конфигурацию
cp -r cursor_workflow_integration/.vscode/ .
```

### 2. Проверить работу
```bash
# Активировать виртуальное окружение
source ./venv/bin/activate

# Проверить AI систему
python -c "from auto_init_ai_system import get_ai_status; print(get_ai_status())"
```

### 3. Использовать в Cursor
1. Открыть проект в Cursor
2. `Ctrl+Shift+P` → `🧠 Initialize AI System`
3. `Ctrl+Shift+P` → `🔍 AI Status Check`

## ✅ Готово!

Теперь у вас есть:
- AI система знающая о 272 модулях проекта
- 17 команд в Command Palette
- Управление сессиями и workflow режимами
- Автоматическое логирование в `ai_system.log`

## 📖 Подробности

Полная документация в `README.md` и папке `docs/` 