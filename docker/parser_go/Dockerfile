# Multi-stage build для Go парсера
FROM golang:1.22-alpine AS go-base
RUN apk add --no-cache git

FROM python:3.11-slim AS python-base

# Установка Go в Python контейнер
COPY --from=go-base /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip

# Копируем только необходимые модули
WORKDIR /app
COPY src/llmstruct/parsers/go_parser.py /app/llmstruct/parsers/
COPY src/llmstruct/generators/go_json_generator.py /app/llmstruct/generators/
COPY src/llmstruct/parsers/__init__.py /app/llmstruct/parsers/
COPY src/llmstruct/generators/__init__.py /app/llmstruct/generators/

# Создаем пустые __init__.py файлы для правильного импорта
RUN touch /app/__init__.py /app/llmstruct/__init__.py

# Создаем упрощенные __init__.py файлы без зависимостей
RUN echo '"""Go parsers for LLMStruct."""' > /app/llmstruct/parsers/__init__.py
RUN echo '"""Go generators for LLMStruct."""' > /app/llmstruct/generators/__init__.py

# Создаем простой CLI скрипт для парсинга
COPY <<'EOF' /app/parse_go.py
#!/usr/bin/env python3
"""
Simple CLI for Go project parsing with llmstruct
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, '/app')

from llmstruct.generators.go_json_generator import generate_go_json


def main():
    parser = argparse.ArgumentParser(description='Parse Go project and generate JSON structure')
    parser.add_argument('project_path', help='Path to Go project directory')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--include-ranges', action='store_true', help='Include line ranges')
    parser.add_argument('--include-hashes', action='store_true', help='Include file hashes')
    parser.add_argument('--goals', nargs='*', help='Project goals')
    
    args = parser.parse_args()
    
    if not Path(args.project_path).exists():
        print(f"Error: Project path {args.project_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = generate_go_json(
            root_dir=args.project_path,
            include_patterns=None,
            exclude_patterns=None,
            gitignore_patterns=None,
            include_ranges=args.include_ranges,
            include_hashes=args.include_hashes,
            goals=args.goals,
            exclude_dirs=None,
        )
        
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"Output written to {args.output}")
        else:
            print(json_output)
            
    except Exception as e:
        print(f"Error parsing project: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
EOF

RUN chmod +x /app/parse_go.py

# Создаем простой тест для проверки работоспособности
COPY <<'EOF' /app/test_parser.py
#!/usr/bin/env python3
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, '/app')

# Создаем тестовый Go файл
test_go_code = '''package main

import (
    "fmt"
    "os"
)

// User represents a user in the system
type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

// NewUser creates a new user
func NewUser(id int, name string) *User {
    return &User{
        ID:   id,
        Name: name,
    }
}

// String returns string representation of user
func (u *User) String() string {
    return fmt.Sprintf("User{ID: %d, Name: %s}", u.ID, u.Name)
}

func main() {
    user := NewUser(1, "Test User")
    fmt.Println(user)
}
'''

def test_parser():
    try:
        from llmstruct.parsers.go_parser import analyze_module
        from llmstruct.generators.go_json_generator import generate_go_json
        
        # Создаем временный файл
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "main.go"
            test_file.write_text(test_go_code)
            
            # Создаем go.mod
            go_mod = Path(temp_dir) / "go.mod"
            go_mod.write_text("module test\n\ngo 1.22\n")
            
            print("Testing Go parser...")
            
            # Тестируем парсер модуля
            result = analyze_module(str(test_file), temp_dir, True, False)
            if result:
                print("✓ Module parsing successful")
                print(f"  Found {len(result['functions'])} functions")
                print(f"  Found {len(result['classes'])} structs")
            else:
                print("✗ Module parsing failed")
                return False
            
            # Тестируем генератор JSON
            json_result = generate_go_json(
                root_dir=temp_dir,
                include_patterns=None,
                exclude_patterns=None,
                gitignore_patterns=None,
                include_ranges=True,
                include_hashes=False,
                goals=["test"],
                exclude_dirs=None,
            )
            
            if json_result and json_result.get('metadata'):
                print("✓ JSON generation successful")
                print(f"  Project: {json_result['metadata']['project_name']}")
                print(f"  Modules: {json_result['metadata']['stats']['modules_count']}")
                return True
            else:
                print("✗ JSON generation failed")
                return False
                
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_parser()
    sys.exit(0 if success else 1)
EOF

RUN chmod +x /app/test_parser.py

# Проверяем что Go установлен
RUN go version

WORKDIR /workspace

ENTRYPOINT ["python", "/app/parse_go.py"] 