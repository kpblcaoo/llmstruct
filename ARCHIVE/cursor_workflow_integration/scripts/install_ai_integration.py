#!/usr/bin/env python3
"""
🚀 Автоматическая установка AI интеграции для Cursor
Устанавливает систему самоанализа AI возможностей в любой проект
"""

import os
import json
import shutil
from pathlib import Path

def install_ai_integration(target_project: str):
    """Установить AI интеграцию в целевой проект"""
    
    print("🚀 УСТАНОВКА AI ИНТЕГРАЦИИ ДЛЯ CURSOR")
    print("=" * 50)
    
    source_root = Path(__file__).parent
    target_root = Path(target_project).resolve()
    
    if not target_root.exists():
        print(f"❌ Целевой проект не найден: {target_root}")
        return False
    
    print(f"📁 Источник: {source_root}")
    print(f"📁 Цель: {target_root}")
    
    # Файлы для копирования
    files_to_copy = [
        (".cursorrules", ".cursorrules"),
        ("auto_init_ai_system.py", "auto_init_ai_system.py"),
        (".vscode/settings.json", ".vscode/settings.json"),
        (".vscode/tasks.json", ".vscode/tasks.json"),
    ]
    
    # Создаем директории
    vscode_dir = target_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    # Копируем файлы
    for source_file, target_file in files_to_copy:
        source_path = source_root / source_file
        target_path = target_root / target_file
        
        if source_path.exists():
            shutil.copy2(source_path, target_path)
            print(f"✅ Скопирован: {source_file}")
        else:
            print(f"⚠️  Не найден: {source_file}")
    
    # Адаптируем файлы под новый проект
    adapt_cursorrules(target_root)
    adapt_auto_init(target_root)
    
    print("\n🎯 УСТАНОВКА ЗАВЕРШЕНА!")
    print("Теперь откройте проект в Cursor и AI система автоматически инициализируется")
    
    return True

def adapt_cursorrules(project_root: Path):
    """Адаптировать .cursorrules под новый проект"""
    
    cursorrules_path = project_root / ".cursorrules"
    if not cursorrules_path.exists():
        return
    
    # Определяем характеристики проекта
    project_name = project_root.name
    has_python = (project_root / "pyproject.toml").exists() or (project_root / "setup.py").exists()
    has_node = (project_root / "package.json").exists()
    has_rust = (project_root / "Cargo.toml").exists()
    
    # Считаем файлы
    python_files = list(project_root.rglob("*.py"))
    js_files = list(project_root.rglob("*.js")) + list(project_root.rglob("*.ts"))
    
    # Обновляем .cursorrules
    content = cursorrules_path.read_text()
    
    # Заменяем информацию о проекте
    content = content.replace(
        "# 🧠 llmstruct AI-Enhanced Development Environment",
        f"# 🧠 {project_name} AI-Enhanced Development Environment"
    )
    
    content = content.replace(
        "'/home/kpblc/projects/github/llmstruct'",
        f"'{project_root}'"
    )
    
    # Обновляем статистику
    if python_files:
        content = content.replace(
            "- **272 модуля** проанализированы",
            f"- **{len(python_files)} Python файлов** найдено"
        )
    
    cursorrules_path.write_text(content)
    print(f"🔧 Адаптирован .cursorrules для проекта {project_name}")

def adapt_auto_init(project_root: Path):
    """Адаптировать auto_init_ai_system.py под новый проект"""
    
    auto_init_path = project_root / "auto_init_ai_system.py"
    if not auto_init_path.exists():
        return
    
    content = auto_init_path.read_text()
    
    # Заменяем пути
    content = content.replace(
        "'/home/kpblc/projects/github/llmstruct'",
        f"'{project_root}'"
    )
    
    # Упрощаем для проектов без llmstruct
    if not (project_root / "src" / "llmstruct").exists():
        # Создаем упрощенную версию
        simplified_content = create_simplified_auto_init(project_root)
        content = simplified_content
    
    auto_init_path.write_text(content)
    print(f"🔧 Адаптирован auto_init_ai_system.py")

def create_simplified_auto_init(project_root: Path) -> str:
    """Создать упрощенную версию auto_init для проектов без llmstruct"""
    
    return f'''#!/usr/bin/env python3
"""
🚀 Автоматическая инициализация AI системы для {project_root.name}
Упрощенная версия для проектов без llmstruct
"""

import os
import sys
import json
from pathlib import Path

AI_STATUS = {{"initialized": False, "error": None}}

def auto_initialize_ai_system():
    """Автоматическая инициализация AI системы"""
    
    global AI_STATUS
    
    if AI_STATUS["initialized"]:
        return True
    
    try:
        project_root = Path(__file__).parent
        
        # Анализируем проект
        python_files = list(project_root.rglob("*.py"))
        js_files = list(project_root.rglob("*.js")) + list(project_root.rglob("*.ts"))
        
        print("🧠 AI System AUTO-INITIALIZED!")
        print(f"   ✅ Project: {project_root.name}")
        print(f"   ✅ Python files: {{len(python_files)}}")
        print(f"   ✅ JS/TS files: {{len(js_files)}}")
        print("   🎯 Basic AI integration ready")
        
        AI_STATUS["initialized"] = True
        return True
        
    except Exception as e:
        AI_STATUS["error"] = str(e)
        print(f"❌ AI System initialization failed: {{e}}")
        return False

def get_ai_status():
    """Получить статус AI системы"""
    if not AI_STATUS["initialized"]:
        auto_initialize_ai_system()
    
    if AI_STATUS["initialized"]:
        return "✅ AI System active for {project_root.name}"
    else:
        return f"❌ AI System not available: {{AI_STATUS.get('error', 'Unknown error')}}"

# Автозапуск при импорте
if __name__ != "__main__":
    auto_initialize_ai_system()

# Если запуск как скрипт
if __name__ == "__main__":
    print("🚀 MANUAL AI SYSTEM INITIALIZATION")
    print("=" * 40)
    auto_initialize_ai_system()
'''

def main():
    """Главная функция установки"""
    
    import sys
    
    if len(sys.argv) != 2:
        print("Использование: python install_ai_integration.py <path_to_project>")
        print("Пример: python install_ai_integration.py /path/to/my-project")
        return
    
    target_project = sys.argv[1]
    success = install_ai_integration(target_project)
    
    if success:
        print("\n🎉 ГОТОВО! Откройте проект в Cursor для активации AI системы")
    else:
        print("\n❌ Установка не удалась")

if __name__ == "__main__":
    main() 