#!/usr/bin/env python3
"""
📁 Bot File Operations Module
Модуль файловых операций для Telegram бота в режиме [code]
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from struct_cache_manager import StructCacheManager

class BotFileOperations:
    """Файловые операции для Telegram бота"""
    
    def __init__(self, work_dir: str = "/tmp/llmstruct_work", simulate_root: bool = True):
        """
        Args:
            work_dir: Рабочая директория (для безопасности используем /tmp)
            simulate_root: Симулировать работу как в корне проекта
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        self.simulate_root = simulate_root
        
        # Если симулируем корень, создаем структуру
        if simulate_root:
            self.setup_simulated_environment()
        
        # Инициализируем кеш менеджер
        self.cache_manager = StructCacheManager()
        
        print(f"📁 BotFileOperations initialized")
        print(f"🗂️ Working directory: {self.work_dir}")
    
    def setup_simulated_environment(self):
        """Создает симулированную среду проекта в /tmp"""
        # Создаем основные директории
        dirs = ["src", "docs", "tests", "scripts", "data", "logs"]
        for dir_name in dirs:
            (self.work_dir / dir_name).mkdir(exist_ok=True)
        
        # Создаем файл README
        readme_content = """# LLMStruct Project (Simulated)
This is a simulated project environment for bot testing.

## Features
- ✅ File reading/writing
- ✅ Directory structure
- ✅ Safe operations in /tmp
"""
        (self.work_dir / "README.md").write_text(readme_content)
        
        print("🏗️ Simulated project environment created")
    
    def list_files(self, path: str = ".") -> Dict[str, Any]:
        """Список файлов в директории"""
        try:
            target_path = self.work_dir / path if path != "." else self.work_dir
            
            if not target_path.exists():
                return {"error": f"Path not found: {path}"}
            
            items = []
            for item in target_path.iterdir():
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                items.append(item_info)
            
            return {
                "path": str(path),
                "items": sorted(items, key=lambda x: (x["type"], x["name"]))
            }
            
        except Exception as e:
            return {"error": f"List files error: {e}"}
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Читает файл"""
        try:
            target_file = self.work_dir / file_path
            
            if not target_file.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not target_file.is_file():
                return {"error": f"Not a file: {file_path}"}
            
            # Проверяем размер файла
            size = target_file.stat().st_size
            if size > 1024 * 1024:  # 1MB limit
                return {"error": f"File too large: {size} bytes (limit: 1MB)"}
            
            content = target_file.read_text(encoding='utf-8')
            
            return {
                "path": file_path,
                "content": content,
                "size": size,
                "lines": len(content.splitlines()),
                "encoding": "utf-8"
            }
            
        except UnicodeDecodeError:
            return {"error": f"Cannot decode file as UTF-8: {file_path}"}
        except Exception as e:
            return {"error": f"Read file error: {e}"}
    
    def write_file(self, file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Записывает файл"""
        try:
            target_file = self.work_dir / file_path
            
            # Создаем директории если нужно
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            if mode == "a":
                # Append mode
                with open(target_file, 'a', encoding='utf-8') as f:
                    f.write(content)
            else:
                # Write mode
                target_file.write_text(content, encoding='utf-8')
            
            size = target_file.stat().st_size
            
            return {
                "path": file_path,
                "mode": mode,
                "size": size,
                "lines": len(content.splitlines()),
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Write file error: {e}"}
    
    def edit_file(self, file_path: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Редактирует файл (замена, вставка, удаление строк)"""
        try:
            target_file = self.work_dir / file_path
            
            if not target_file.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Читаем файл
            lines = target_file.read_text(encoding='utf-8').splitlines()
            original_count = len(lines)
            
            op_type = operation.get("type", "replace")
            
            if op_type == "replace":
                # Замена строки
                line_num = operation.get("line", 1) - 1  # 0-based
                new_content = operation.get("content", "")
                
                if 0 <= line_num < len(lines):
                    old_line = lines[line_num]
                    lines[line_num] = new_content
                    
                    # Записываем обратно
                    target_file.write_text("\n".join(lines) + "\n", encoding='utf-8')
                    
                    return {
                        "path": file_path,
                        "operation": "replace",
                        "line": line_num + 1,
                        "old_content": old_line,
                        "new_content": new_content,
                        "total_lines": len(lines)
                    }
                else:
                    return {"error": f"Line number out of range: {line_num + 1}"}
            
            elif op_type == "insert":
                # Вставка строки
                line_num = operation.get("line", len(lines) + 1) - 1
                new_content = operation.get("content", "")
                
                lines.insert(line_num, new_content)
                target_file.write_text("\n".join(lines) + "\n", encoding='utf-8')
                
                return {
                    "path": file_path,
                    "operation": "insert",
                    "line": line_num + 1,
                    "content": new_content,
                    "total_lines": len(lines)
                }
            
            elif op_type == "append":
                # Добавление в конец
                new_content = operation.get("content", "")
                lines.append(new_content)
                target_file.write_text("\n".join(lines) + "\n", encoding='utf-8')
                
                return {
                    "path": file_path,
                    "operation": "append",
                    "content": new_content,
                    "total_lines": len(lines)
                }
            
            elif op_type == "find_replace":
                # Поиск и замена
                find_text = operation.get("find", "")
                replace_text = operation.get("replace", "")
                
                content = "\n".join(lines)
                new_content = content.replace(find_text, replace_text)
                target_file.write_text(new_content, encoding='utf-8')
                
                changes = content.count(find_text)
                
                return {
                    "path": file_path,
                    "operation": "find_replace",
                    "find": find_text,
                    "replace": replace_text,
                    "changes": changes,
                    "total_lines": len(new_content.splitlines())
                }
            
            else:
                return {"error": f"Unknown operation type: {op_type}"}
                
        except Exception as e:
            return {"error": f"Edit file error: {e}"}
    
    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """Создает директорию"""
        try:
            target_dir = self.work_dir / dir_path
            target_dir.mkdir(parents=True, exist_ok=True)
            
            return {
                "path": dir_path,
                "status": "created",
                "exists": True
            }
            
        except Exception as e:
            return {"error": f"Create directory error: {e}"}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Удаляет файл"""
        try:
            target_path = self.work_dir / file_path
            
            if not target_path.exists():
                return {"error": f"Path not found: {file_path}"}
            
            if target_path.is_file():
                target_path.unlink()
                return {"path": file_path, "type": "file", "status": "deleted"}
            elif target_path.is_dir():
                shutil.rmtree(target_path)
                return {"path": file_path, "type": "directory", "status": "deleted"}
            else:
                return {"error": f"Unknown path type: {file_path}"}
                
        except Exception as e:
            return {"error": f"Delete error: {e}"}
    
    def copy_file(self, src_path: str, dst_path: str) -> Dict[str, Any]:
        """Копирует файл"""
        try:
            src_file = self.work_dir / src_path
            dst_file = self.work_dir / dst_path
            
            if not src_file.exists():
                return {"error": f"Source file not found: {src_path}"}
            
            # Создаем директории если нужно
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_file, dst_file)
            
            return {
                "src": src_path,
                "dst": dst_path,
                "size": dst_file.stat().st_size,
                "status": "copied"
            }
            
        except Exception as e:
            return {"error": f"Copy error: {e}"}
    
    def search_struct(self, query: str, search_type: str = "all") -> Dict[str, Any]:
        """Поиск в struct.json через кеш"""
        try:
            results = self.cache_manager.smart_search(query, search_type)
            
            return {
                "query": query,
                "search_type": search_type,
                "results": results,
                "total_results": sum(len(results[key]) for key in results)
            }
            
        except Exception as e:
            return {"error": f"Struct search error: {e}"}
    
    def get_struct_stats(self) -> Dict[str, Any]:
        """Получает статистику struct.json кеша"""
        try:
            stats = self.cache_manager.get_cache_stats()
            return stats
        except Exception as e:
            return {"error": f"Struct stats error: {e}"}
    
    def invalidate_struct_cache(self) -> Dict[str, Any]:
        """Инвалидирует кеш struct.json"""
        try:
            self.cache_manager.invalidate_cache()
            return {"status": "cache_invalidated"}
        except Exception as e:
            return {"error": f"Cache invalidation error: {e}"}
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Получает статус рабочего пространства"""
        try:
            total_files = 0
            total_dirs = 0
            total_size = 0
            
            for item in self.work_dir.rglob("*"):
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size
                elif item.is_dir():
                    total_dirs += 1
            
            return {
                "work_directory": str(self.work_dir),
                "simulate_root": self.simulate_root,
                "total_files": total_files,
                "total_directories": total_dirs,
                "total_size": total_size,
                "cache_status": self.cache_manager.get_cache_stats(),
                "status": "operational"
            }
            
        except Exception as e:
            return {"error": f"Workspace status error: {e}"}

def test_file_operations():
    """Тестирование файловых операций"""
    print("🧪 Testing Bot File Operations...")
    
    ops = BotFileOperations()
    
    # Тест создания файла
    result = ops.write_file("test.txt", "Hello from bot!\nLine 2\nLine 3")
    print(f"📝 Write test: {result}")
    
    # Тест чтения
    result = ops.read_file("test.txt")
    print(f"📖 Read test: {result.get('lines', 0)} lines")
    
    # Тест редактирования
    result = ops.edit_file("test.txt", {
        "type": "replace",
        "line": 2,
        "content": "EDITED Line 2"
    })
    print(f"✏️ Edit test: {result}")
    
    # Тест поиска в struct
    result = ops.search_struct("context", "functions")
    print(f"🔍 Struct search: {result.get('total_results', 0)} results")
    
    # Статус workspace
    status = ops.get_workspace_status()
    print(f"📊 Workspace: {status['total_files']} files, {status['total_size']} bytes")
    
    print("✅ All file operations tested!")

if __name__ == "__main__":
    test_file_operations() 