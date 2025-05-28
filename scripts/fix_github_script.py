#!/usr/bin/env python3
"""
Quick fix for GitHub issues creation script
Исправляет проблемы с загрузкой JSON и структурой данных
"""

import json
import os
from pathlib import Path

def fix_json_loading():
    """Исправить загрузку JSON данных"""
    
    # Читаем оригинальный скрипт
    script_path = Path("scripts/create_github_issues.py")
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправления
    fixes = [
        # Исправление URL
        ('f"https://api.github.com/repos/{owner}/{repo}"', 'f"https://api.github.com/repos/{self.owner}/{self.repo}"'),
        
        # Исправление загрузки JSON
        ('epics_data = load_epics_data()', '''epics_data = load_epics_data()
    if not epics_data:
        return
    epics_list = epics_data.get('epics', epics_data)  # Handle both structures'''),
        
        # Исправление обработки эпиков
        ('for epic_data in epics_data:', 'for epic_data in epics_list:')
    ]
    
    # Применяем исправления
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Записываем исправленный скрипт
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ GitHub script fixed!")

if __name__ == "__main__":
    fix_json_loading() 