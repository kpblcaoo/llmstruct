# 🧠 AI Integration Setup Guide for Cursor

Руководство по установке системы самоанализа AI возможностей в любой проект для Cursor IDE.

## 🚀 Quick Setup (5 минут)

### 1. Скопируйте файлы в ваш проект:

```bash
# Основные файлы
cp .cursorrules /path/to/your/project/
cp auto_init_ai_system.py /path/to/your/project/

# VS Code настройки  
mkdir -p /path/to/your/project/.vscode
cp .vscode/settings.json /path/to/your/project/.vscode/
cp .vscode/tasks.json /path/to/your/project/.vscode/
```

### 2. Адаптируйте под ваш проект:

**В `.cursorrules`:**
- Замените `llmstruct` на имя вашего проекта
- Обновите пути к модулям
- Адаптируйте статистику (количество файлов/модулей)

**В `auto_init_ai_system.py`:**
- Замените пути на пути вашего проекта
- Упростите функции если нет llmstruct модулей

### 3. Откройте проект в Cursor:
- AI система автоматически инициализируется
- Терминал покажет статус инициализации
- В чате Cursor вы сможете использовать AI самоанализ

## 📋 Подробная установка

### Шаг 1: Структура файлов

Добавьте в корень вашего проекта:

```
your-project/
├── .cursorrules                 # Контекст для Claude
├── auto_init_ai_system.py       # Автоинициализация
└── .vscode/
    ├── settings.json           # Настройки проекта
    └── tasks.json              # Задачи для AI команд
```

### Шаг 2: Настройка .cursorrules

Минимальный .cursorrules для любого проекта:

```markdown
# 🧠 Your Project AI-Enhanced Environment

## 🔧 AI System Status
**СИСТЕМА АКТИВНА**: AI может анализировать проект и помогать в разработке

## 🎯 Рабочий процесс
### При вопросах о проекте:
1. Используй автоинициализацию AI системы
2. Анализируй структуру проекта
3. Предлагай оптимальные решения

## 🚀 Команды для пользователя
```bash
# Статус AI системы
python auto_init_ai_system.py

# Анализ проекта
find . -name "*.py" | wc -l  # Для Python
find . -name "*.js" -o -name "*.ts" | wc -l  # Для JS/TS
```
```

### Шаг 3: Упрощенный auto_init_ai_system.py

Для проектов без llmstruct:

```python
#!/usr/bin/env python3
"""Auto AI System for Cursor"""

import os
from pathlib import Path

def auto_initialize_ai_system():
    project_root = Path(__file__).parent
    
    # Анализ проекта
    python_files = list(project_root.rglob("*.py"))
    js_files = list(project_root.rglob("*.js")) + list(project_root.rglob("*.ts"))
    
    print("🧠 AI System AUTO-INITIALIZED!")
    print(f"   ✅ Project: {project_root.name}")
    print(f"   ✅ Python files: {len(python_files)}")
    print(f"   ✅ JS/TS files: {len(js_files)}")
    print("   🎯 AI integration ready")
    
    return True

if __name__ == "__main__":
    auto_initialize_ai_system()
```

### Шаг 4: Базовые VS Code настройки

`.vscode/settings.json`:
```json
{
  "editor.inlineSuggest.enabled": true,
  "editor.quickSuggestions": {
    "other": true,
    "comments": false,
    "strings": true
  },
  "files.associations": {
    ".cursorrules": "markdown"
  }
}
```

`.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🧠 Initialize AI System",
            "type": "shell",
            "command": "python",
            "args": ["auto_init_ai_system.py"],
            "group": "build",
            "runOptions": {
                "runOn": "folderOpen"
            }
        }
    ]
}
```

## 🎯 Возможности после установки

### В Cursor чате:
- "Покажи статус AI системы" → использует auto_init
- "Проанализируй структуру проекта" → сканирует файлы
- "Найди функции с..." → поиск по коду

### Command Palette (Ctrl+Shift+P):
- `🧠 Initialize AI System` - инициализация
- Любые добавленные вами tasks

### Автоматически при открытии:
- AI система инициализируется
- Анализируется структура проекта
- Готов контекст для Claude

## 🔧 Кастомизация

### Для Python проектов:
```python
# В auto_init_ai_system.py добавьте:
def analyze_python_project():
    # Поиск requirements.txt, setup.py, pyproject.toml
    # Анализ imports
    # Подсчет классов/функций
```

### Для JavaScript/Node.js:
```python
def analyze_js_project():
    # Поиск package.json
    # Анализ dependencies
    # Подсчет компонентов
```

### Для любого языка:
```python
def analyze_project():
    # Общий анализ файловой структуры
    # Git анализ
    # Размер проекта
```

## ✅ Проверка установки

1. Откройте проект в Cursor
2. Должно появиться: "🧠 AI System AUTO-INITIALIZED!"
3. В чате попробуйте: "Покажи статус проекта"
4. Claude должен понимать структуру вашего проекта

## 🎉 Готово!

Теперь у вас есть AI система которая:
- ✅ Знает о структуре проекта
- ✅ Может анализировать код
- ✅ Интегрируется с Cursor
- ✅ Помогает в разработке 