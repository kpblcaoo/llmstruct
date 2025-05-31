#!/usr/bin/env python3
"""
Setup script for Continue VS Code extension configuration
Заменяет переменные в config.template.json на значения из .env
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

def load_env_vars() -> Dict[str, str]:
    """Загружает переменные из .env файла"""
    env_vars = {}
    
    # Ищем .env файл в корне проекта
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
    
    # Добавляем переменные окружения
    env_vars.update(os.environ)
    
    return env_vars

def substitute_variables(config: Any, env_vars: Dict[str, str]) -> Any:
    """Заменяет переменные ${VAR:-default} на значения из env_vars"""
    if isinstance(config, dict):
        return {k: substitute_variables(v, env_vars) for k, v in config.items()}
    elif isinstance(config, list):
        return [substitute_variables(item, env_vars) for item in config]
    elif isinstance(config, str):
        # Заменяем переменные вида ${VAR:-default}
        if '${' in config:
            import re
            def replace_var(match):
                var_expr = match.group(1)
                if ':-' in var_expr:
                    var_name, default = var_expr.split(':-', 1)
                else:
                    var_name, default = var_expr, ""
                
                return env_vars.get(var_name, default)
            
            config = re.sub(r'\$\{([^}]+)\}', replace_var, config)
        
        return config
    else:
        return config

def main():
    """Основная функция"""
    current_dir = Path(__file__).parent
    template_file = current_dir / ".continue" / "config.template.json"
    config_file = current_dir / ".continue" / "config.json"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        sys.exit(1)
    
    # Загружаем переменные окружения
    env_vars = load_env_vars()
    
    # Загружаем шаблон
    with open(template_file, 'r') as f:
        template_config = json.load(f)
    
    # Заменяем переменные
    final_config = substitute_variables(template_config, env_vars)
    
    # Создаем директорию если не существует
    config_file.parent.mkdir(exist_ok=True)
    
    # Сохраняем финальную конфигурацию
    with open(config_file, 'w') as f:
        json.dump(final_config, f, indent=2)
    
    print(f"✅ Continue configuration created: {config_file}")
    print(f"🔧 API Base: {env_vars.get('LLMSTRUCT_API_BASE', 'http://localhost:8000')}")
    print(f"🔑 API Key: {env_vars.get('LLMSTRUCT_API_KEY', 'dev-key')}")
    
    # Показываем доступные переменные
    print("\n📋 Available environment variables:")
    print("- LLMSTRUCT_API_BASE (default: http://localhost:8000)")
    print("- LLMSTRUCT_API_KEY (default: dev-key)")
    print("\n💡 Create .env file in project root to customize settings")

if __name__ == "__main__":
    main() 