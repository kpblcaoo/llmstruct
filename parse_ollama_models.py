#!/usr/bin/env python3
"""
Парсер списка моделей Ollama для структурированного анализа
"""
import re
import json

def parse_ollama_models(file_path):
    """Парсит файл со списком моделей Ollama и возвращает структурированные данные"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Разделяем на блоки моделей
    # Каждая модель начинается с имени (строчные буквы, цифры, дефисы, точки)
    # и заканчивается строкой с "Updated"
    
    models = []
    current_model = None
    current_block = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Проверяем, начинается ли новая модель
        if re.match(r'^[a-z][a-z0-9\-\.]*$', line) and len(line) > 2:
            # Сохраняем предыдущую модель если была
            if current_model:
                models.append(parse_model_block(current_model, current_block))
            
            # Начинаем новую модель
            current_model = line
            current_block = []
        
        elif current_model:
            current_block.append(line)
    
    # Сохраняем последнюю модель
    if current_model:
        models.append(parse_model_block(current_model, current_block))
    
    return models

def parse_model_block(name, block):
    """Парсит блок информации о модели"""
    
    model_data = {
        'name': name,
        'description': '',
        'capabilities': [],
        'sizes': [],
        'pulls': 0,
        'tags': 0,
        'updated': ''
    }
    
    # Ищем описание (обычно первая содержательная строка)
    description_found = False
    for line in block:
        if line and not description_found and not line.isdigit() and 'Updated' not in line:
            if not re.match(r'^(vision|tools|thinking|embedding|\d+[bk]?)$', line):
                model_data['description'] = line
                description_found = True
                break
    
    # Ищем capabilities (vision, tools, thinking, embedding)
    capabilities = []
    for line in block:
        if line in ['vision', 'tools', 'thinking', 'embedding']:
            capabilities.append(line)
    model_data['capabilities'] = capabilities
    
    # Ищем размеры моделей (например: 1b, 7b, 70b, 405b)
    sizes = []
    for line in block:
        if re.match(r'^\d+[bkm]?$', line):
            sizes.append(line)
    model_data['sizes'] = sizes
    
    # Ищем количество pulls (строка с "Pulls")
    for i, line in enumerate(block):
        if 'Pulls' in line and i > 0:
            prev_line = block[i-1]
            if prev_line.replace('.', '').replace('M', '').replace('K', '').isdigit():
                model_data['pulls'] = prev_line
                break
    
    # Ищем количество tags
    for i, line in enumerate(block):
        if 'Tags' in line and i > 0:
            prev_line = block[i-1]
            if prev_line.isdigit():
                model_data['tags'] = int(prev_line)
                break
    
    # Ищем дату обновления
    for i, line in enumerate(block):
        if 'Updated' in line and i < len(block) - 1:
            next_line = block[i+1]
            model_data['updated'] = next_line
            break
    
    return model_data

def categorize_models(models):
    """Категоризирует модели по возможностям и применению"""
    
    categories = {
        'vision': [],
        'code': [],
        'embedding': [],
        'reasoning': [],
        'general': [],
        'small_efficient': [],
        'large_powerful': []
    }
    
    for model in models:
        name = model['name'].lower()
        description = model['description'].lower()
        capabilities = model['capabilities']
        
        # Vision модели
        if 'vision' in capabilities or 'vision' in name or 'llava' in name or 'minicpm-v' in name:
            categories['vision'].append(model)
        
        # Code модели
        elif ('code' in name or 'coder' in name or 'starcoder' in name or 
              'codellama' in name or 'codegemma' in name or 'sqlcoder' in name or
              'code generation' in description or 'coding' in description):
            categories['code'].append(model)
        
        # Embedding модели  
        elif 'embedding' in capabilities or 'embed' in name:
            categories['embedding'].append(model)
        
        # Reasoning модели
        elif ('thinking' in capabilities or 'reasoning' in description or 
              'qwq' in name or 'deepseek-r1' in name):
            categories['reasoning'].append(model)
        
        # Маленькие эффективные модели (до 3B)
        elif any(size in ['0.5b', '1b', '1.1b', '1.5b', '2b', '3b'] for size in model['sizes']):
            categories['small_efficient'].append(model)
        
        # Большие мощные модели (70B+)
        elif any(size in ['70b', '405b', '671b'] for size in model['sizes']):
            categories['large_powerful'].append(model)
        
        # Остальные - общего назначения
        else:
            categories['general'].append(model)
    
    return categories

def analyze_for_rtx3060ti(models):
    """Анализирует модели с точки зрения совместимости с RTX 3060 Ti (8GB VRAM)"""
    
    compatible_models = []
    
    for model in models:
        max_size = 0
        for size in model['sizes']:
            if size.endswith('b'):
                size_num = float(size[:-1])
                max_size = max(max_size, size_num)
        
        # RTX 3060 Ti может запускать модели до ~7B комфортно
        if max_size <= 8:
            compatibility = 'excellent' if max_size <= 3 else 'good' if max_size <= 7 else 'possible'
            compatible_models.append({
                **model,
                'max_size_b': max_size,
                'rtx3060ti_compatibility': compatibility
            })
    
    return sorted(compatible_models, key=lambda x: x['max_size_b'])

if __name__ == '__main__':
    print("Парсинг списка моделей Ollama...")
    
    models = parse_ollama_models('tmp/ollama_list.txt')
    print(f"Найдено {len(models)} моделей")
    
    categories = categorize_models(models)
    print("\nКатегории моделей:")
    for cat, models_list in categories.items():
        print(f"  {cat}: {len(models_list)} моделей")
    
    compatible = analyze_for_rtx3060ti(models)
    print(f"\nСовместимых с RTX 3060 Ti: {len(compatible)} моделей")
    
    # Создаем структурированный JSON для анализа
    analysis_data = {
        'total_models': len(models),
        'categories': {cat: len(models_list) for cat, models_list in categories.items()},
        'rtx3060ti_compatible': len(compatible),
        'top_models_by_category': {},
        'recommended_for_llmstruct': []
    }
    
    # Топ-3 в каждой категории
    for cat, models_list in categories.items():
        if models_list:
            sorted_models = sorted(models_list, key=lambda x: float(x['pulls'].replace('M', '').replace('K', '').replace('.', '')) if isinstance(x['pulls'], str) and x['pulls'].replace('M', '').replace('K', '').replace('.', '').isdigit() else 0, reverse=True)
            analysis_data['top_models_by_category'][cat] = sorted_models[:3]
    
    # Рекомендации для LLMStruct проекта
    recommendations = []
    
    # Vision для диаграмм
    vision_models = [m for m in compatible if 'vision' in m['capabilities']][:3]
    if vision_models:
        recommendations.extend([{**m, 'recommended_for': 'diagram_generation'} for m in vision_models])
    
    # Code для cleanup и анализа
    code_models = [m for m in compatible if 'code' in m['name'].lower()][:3]
    if code_models:
        recommendations.extend([{**m, 'recommended_for': 'code_analysis_cleanup'} for m in code_models])
    
    # Embedding для поиска
    embed_models = [m for m in compatible if 'embedding' in m['capabilities']][:2]
    if embed_models:
        recommendations.extend([{**m, 'recommended_for': 'semantic_search'} for m in embed_models])
    
    analysis_data['recommended_for_llmstruct'] = recommendations
    
    # Сохраняем анализ
    with open('grok_consultations_series_2/ollama_models_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\nАнализ сохранен в grok_consultations_series_2/ollama_models_analysis.json")
    print(f"Рекомендовано для LLMStruct: {len(recommendations)} моделей") 