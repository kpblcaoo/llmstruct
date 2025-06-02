#!/usr/bin/env python3
"""
🚀 Smart struct.json Cache Manager for [code] Mode
Оптимизированное кеширование для быстрого доступа к структуре проекта
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class StructCacheManager:
    """Умный менеджер кеша для struct.json в режиме [code]"""
    
    def __init__(self, struct_file: str = "struct.json"):
        self.struct_file = Path(struct_file)
        self.cache_dir = Path(".llmstruct_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Файлы кеша
        self.module_index = self.cache_dir / "module_index.json"
        self.function_index = self.cache_dir / "function_index.json" 
        self.class_index = self.cache_dir / "class_index.json"
        self.search_cache = self.cache_dir / "search_cache.json"
        self.metadata_cache = self.cache_dir / "metadata.json"
        
        print("🗃️ StructCacheManager initialized")
    
    def get_file_hash(self) -> str:
        """Получает хеш файла struct.json для проверки изменений"""
        if not self.struct_file.exists():
            return ""
        
        with open(self.struct_file, 'rb') as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()
    
    def is_cache_valid(self) -> bool:
        """Проверяет валидность кеша"""
        if not self.metadata_cache.exists():
            return False
        
        try:
            with open(self.metadata_cache, 'r') as f:
                metadata = json.load(f)
            
            current_hash = self.get_file_hash()
            cached_hash = metadata.get('file_hash', '')
            
            return current_hash == cached_hash
        except Exception:
            return False
    
    def build_cache(self) -> bool:
        """Строит полный кеш из struct.json"""
        if not self.struct_file.exists():
            print("❌ struct.json not found")
            return False
        
        print("🔄 Building cache from struct.json...")
        start_time = time.time()
        
        try:
            with open(self.struct_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Индекс модулей
            modules = data.get('modules', [])
            module_index = {}
            for module in modules:
                name = module.get('name', 'unknown')
                module_index[name] = {
                    'path': module.get('path', ''),
                    'functions': [f.get('name', '') for f in module.get('functions', [])],
                    'classes': [c.get('name', '') for c in module.get('classes', [])],
                    'imports': module.get('imports', []),
                    'exports': module.get('exports', [])
                }
            
            # Индекс функций
            function_index = {}
            for module in modules:
                module_name = module.get('name', 'unknown')
                for func in module.get('functions', []):
                    func_name = func.get('name', '')
                    if func_name:
                        function_index[func_name] = {
                            'module': module_name,
                            'path': module.get('path', ''),
                            'line': func.get('line', 0),
                            'args': func.get('args', []),
                            'description': func.get('description', '')
                        }
            
            # Индекс классов
            class_index = {}
            for module in modules:
                module_name = module.get('name', 'unknown')
                for cls in module.get('classes', []):
                    cls_name = cls.get('name', '')
                    if cls_name:
                        class_index[cls_name] = {
                            'module': module_name,
                            'path': module.get('path', ''),
                            'line': cls.get('line', 0),
                            'methods': [m.get('name', '') for m in cls.get('methods', [])],
                            'properties': cls.get('properties', [])
                        }
            
            # Сохраняем индексы
            with open(self.module_index, 'w', encoding='utf-8') as f:
                json.dump(module_index, f, ensure_ascii=False, indent=2)
            
            with open(self.function_index, 'w', encoding='utf-8') as f:
                json.dump(function_index, f, ensure_ascii=False, indent=2)
            
            with open(self.class_index, 'w', encoding='utf-8') as f:
                json.dump(class_index, f, ensure_ascii=False, indent=2)
            
            # Метаданные кеша
            metadata = {
                'created_at': datetime.now().isoformat(),
                'file_hash': self.get_file_hash(),
                'modules_count': len(module_index),
                'functions_count': len(function_index),
                'classes_count': len(class_index),
                'build_time': time.time() - start_time,
                'cache_version': '1.0'
            }
            
            with open(self.metadata_cache, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Инициализируем пустой кеш поиска
            with open(self.search_cache, 'w', encoding='utf-8') as f:
                json.dump({}, f)
            
            build_time = time.time() - start_time
            print(f"✅ Cache built successfully in {build_time:.2f}s")
            print(f"📁 Modules: {len(module_index)}")
            print(f"🔧 Functions: {len(function_index)}")
            print(f"🏗️ Classes: {len(class_index)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Cache building error: {e}")
            return False
    
    def search_modules(self, query: str) -> List[Dict]:
        """Быстрый поиск модулей"""
        if not self.is_cache_valid():
            self.build_cache()
        
        try:
            with open(self.module_index, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            
            results = []
            query_lower = query.lower()
            
            for name, info in modules.items():
                if query_lower in name.lower():
                    results.append({
                        'name': name,
                        'path': info['path'],
                        'functions_count': len(info['functions']),
                        'classes_count': len(info['classes'])
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Module search error: {e}")
            return []
    
    def search_functions(self, query: str) -> List[Dict]:
        """Быстрый поиск функций"""
        if not self.is_cache_valid():
            self.build_cache()
        
        try:
            with open(self.function_index, 'r', encoding='utf-8') as f:
                functions = json.load(f)
            
            results = []
            query_lower = query.lower()
            
            for name, info in functions.items():
                if query_lower in name.lower():
                    results.append({
                        'name': name,
                        'module': info['module'],
                        'path': info['path'],
                        'line': info['line'],
                        'args': info['args']
                    })
            
            return sorted(results, key=lambda x: x['name'])
            
        except Exception as e:
            print(f"❌ Function search error: {e}")
            return []
    
    def search_classes(self, query: str) -> List[Dict]:
        """Быстрый поиск классов"""
        if not self.is_cache_valid():
            self.build_cache()
        
        try:
            with open(self.class_index, 'r', encoding='utf-8') as f:
                classes = json.load(f)
            
            results = []
            query_lower = query.lower()
            
            for name, info in classes.items():
                if query_lower in name.lower():
                    results.append({
                        'name': name,
                        'module': info['module'],
                        'path': info['path'],
                        'line': info['line'],
                        'methods_count': len(info['methods'])
                    })
            
            return sorted(results, key=lambda x: x['name'])
            
        except Exception as e:
            print(f"❌ Class search error: {e}")
            return []
    
    def get_module_details(self, module_name: str) -> Optional[Dict]:
        """Получает детали модуля"""
        if not self.is_cache_valid():
            self.build_cache()
        
        try:
            with open(self.module_index, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            
            return modules.get(module_name)
            
        except Exception as e:
            print(f"❌ Module details error: {e}")
            return None
    
    def get_cache_stats(self) -> Dict:
        """Получает статистику кеша"""
        if not self.metadata_cache.exists():
            return {'status': 'no_cache'}
        
        try:
            with open(self.metadata_cache, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            metadata['is_valid'] = self.is_cache_valid()
            metadata['status'] = 'valid' if metadata['is_valid'] else 'outdated'
            
            return metadata
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def invalidate_cache(self):
        """Инвалидирует кеш"""
        cache_files = [
            self.module_index,
            self.function_index,
            self.class_index,
            self.search_cache,
            self.metadata_cache
        ]
        
        for cache_file in cache_files:
            if cache_file.exists():
                cache_file.unlink()
        
        print("🗑️ Cache invalidated")
    
    def smart_search(self, query: str, search_type: str = "all") -> Dict:
        """Умный поиск по всем индексам с кешированием результатов"""
        # Проверяем кеш поиска
        cache_key = f"{search_type}:{query.lower()}"
        
        try:
            if self.search_cache.exists():
                with open(self.search_cache, 'r', encoding='utf-8') as f:
                    search_cache = json.load(f)
                
                if cache_key in search_cache:
                    print(f"🚀 Cache hit for: {query}")
                    return search_cache[cache_key]
        except Exception:
            search_cache = {}
        
        # Выполняем поиск
        results = {'modules': [], 'functions': [], 'classes': []}
        
        if search_type in ["all", "modules"]:
            results['modules'] = self.search_modules(query)
        
        if search_type in ["all", "functions"]:
            results['functions'] = self.search_functions(query)
        
        if search_type in ["all", "classes"]:
            results['classes'] = self.search_classes(query)
        
        # Сохраняем в кеш поиска
        try:
            search_cache[cache_key] = results
            with open(self.search_cache, 'w', encoding='utf-8') as f:
                json.dump(search_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Search cache save error: {e}")
        
        return results

def test_cache_performance():
    """Тест производительности кеша"""
    print("🏁 Testing cache performance...")
    
    cache_manager = StructCacheManager()
    
    # Тест построения кеша
    start = time.time()
    success = cache_manager.build_cache()
    build_time = time.time() - start
    
    if not success:
        print("❌ Cache build failed")
        return
    
    print(f"⏱️ Cache build time: {build_time:.2f}s")
    
    # Тест поиска
    test_queries = ["test", "context", "system", "manager", "ai"]
    
    for query in test_queries:
        start = time.time()
        results = cache_manager.smart_search(query)
        search_time = time.time() - start
        
        total_results = sum(len(results[key]) for key in results)
        print(f"🔍 '{query}': {total_results} results in {search_time:.3f}s")
    
    # Статистика кеша
    stats = cache_manager.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"  Status: {stats.get('status', 'unknown')}")
    print(f"  Modules: {stats.get('modules_count', 0)}")
    print(f"  Functions: {stats.get('functions_count', 0)}")
    print(f"  Classes: {stats.get('classes_count', 0)}")

if __name__ == "__main__":
    test_cache_performance() 