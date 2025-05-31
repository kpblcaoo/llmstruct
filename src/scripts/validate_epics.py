#!/usr/bin/env python3
"""
Epic Data Validator
Проверяет корректность данных эпиков перед созданием GitHub issues
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def validate_epic_structure(epic: Dict[str, Any]) -> List[str]:
    """Проверить структуру эпика"""
    errors = []
    
    required_fields = [
        'id', 'name', 'status', 'priority', 'estimate', 
        'description', 'done_criteria', 'metrics', 'tasks'
    ]
    
    for field in required_fields:
        if field not in epic:
            errors.append(f"Missing required field: {field}")
    
    # Проверка типов
    if 'id' in epic and not isinstance(epic['id'], int):
        errors.append("Field 'id' must be integer")
    
    if 'tasks' in epic and not isinstance(epic['tasks'], list):
        errors.append("Field 'tasks' must be list")
    
    if 'done_criteria' in epic and not isinstance(epic['done_criteria'], list):
        errors.append("Field 'done_criteria' must be list")
    
    return errors

def validate_task_structure(task: Dict[str, Any], epic_id: int) -> List[str]:
    """Проверить структуру задачи"""
    errors = []
    
    required_fields = ['id', 'name', 'priority', 'estimate', 'description', 'acceptance_criteria']
    
    for field in required_fields:
        if field not in task:
            errors.append(f"Epic {epic_id}, Task {task.get('id', '?')}: Missing field {field}")
    
    if 'id' in task and not isinstance(task['id'], int):
        errors.append(f"Epic {epic_id}, Task {task.get('id', '?')}: 'id' must be integer")
    
    if 'acceptance_criteria' in task and not isinstance(task['acceptance_criteria'], list):
        errors.append(f"Epic {epic_id}, Task {task.get('id', '?')}: 'acceptance_criteria' must be list")
    
    return errors

def validate_priorities(data: Dict[str, Any]) -> List[str]:
    """Проверить валидность приоритетов"""
    errors = []
    valid_priorities = ['🔥 CRITICAL', '🔥 HIGH', '🟡 MEDIUM', '🟢 LOW']
    
    for epic in data.get('epics', []):
        if epic.get('priority') not in valid_priorities:
            errors.append(f"Epic {epic.get('id')}: Invalid priority '{epic.get('priority')}'")
        
        for task in epic.get('tasks', []):
            if task.get('priority') not in valid_priorities:
                errors.append(f"Epic {epic.get('id')}, Task {task.get('id')}: Invalid priority '{task.get('priority')}'")
    
    return errors

def validate_task_ids(data: Dict[str, Any]) -> List[str]:
    """Проверить уникальность ID задач"""
    errors = []
    seen_ids = set()
    
    for epic in data.get('epics', []):
        for task in epic.get('tasks', []):
            task_id = task.get('id')
            if task_id in seen_ids:
                errors.append(f"Duplicate task ID: {task_id}")
            seen_ids.add(task_id)
    
    return errors

def main():
    """Основная функция валидации"""
    epics_file = Path("epics/epics_data.json")
    
    if not epics_file.exists():
        print("❌ File epics/epics_data.json not found!")
        sys.exit(1)
    
    try:
        with open(epics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        sys.exit(1)
    
    print("🔍 Validating epics data...")
    
    all_errors = []
    
    # Проверка базовой структуры
    if 'epics' not in data:
        all_errors.append("Missing 'epics' key in JSON")
    elif not isinstance(data['epics'], list):
        all_errors.append("'epics' must be a list")
    else:
        # Проверка каждого эпика
        for epic in data['epics']:
            errors = validate_epic_structure(epic)
            all_errors.extend(errors)
            
            # Проверка задач эпика
            for task in epic.get('tasks', []):
                task_errors = validate_task_structure(task, epic.get('id', '?'))
                all_errors.extend(task_errors)
    
    # Дополнительные проверки
    all_errors.extend(validate_priorities(data))
    all_errors.extend(validate_task_ids(data))
    
    # Результат
    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} errors:")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("✅ Validation successful!")
        print(f"Found {len(data['epics'])} epics with {sum(len(e.get('tasks', [])) for e in data['epics'])} total tasks")

if __name__ == "__main__":
    main() 