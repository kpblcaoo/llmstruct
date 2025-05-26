#!/usr/bin/env python3
"""
JSON Schema Validation Script for llmstruct
Validates all enhanced JSON files against their appropriate schemas.
Part of TSK-130 implementation.
"""

import json
import sys
from jsonschema import validate, ValidationError, draft7_format_checker
import os

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def load_json(file_path):
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}❌ JSON Parse Error in {file_path}: {e}{Colors.ENDC}")
        return None
    except FileNotFoundError:
        print(f"{Colors.YELLOW}⚠️  File not found: {file_path}{Colors.ENDC}")
        return None


def validate_json_against_schema(json_data, schema_data, file_name):
    """Validate JSON data against schema."""
    try:
        validate(
            instance=json_data,
            schema=schema_data,
            format_checker=draft7_format_checker)
        print(f"{Colors.GREEN}✅ {file_name}: Valid{Colors.ENDC}")
        return True
    except ValidationError as e:
        print(f"{Colors.RED}❌ {file_name}: Validation Error{Colors.ENDC}")
        print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        print(f"   Error: {e.message}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error in {file_name}: {e}{Colors.ENDC}")
        return False


def main():
    """Main execution flow for validating JSON files against schemas."""
    if len(sys.argv) < 3:
        print(f"{Colors.BLUE}Usage: validate_schemas.py <schema_directory> <json_directory>{Colors.ENDC}")
        sys.exit(1)

    schema_dir = sys.argv[1]
    json_dir = sys.argv[2]

    if not os.path.isdir(schema_dir):
        print(f"{Colors.RED}Error: Schema directory {schema_dir} does not exist.{Colors.ENDC}")
        sys.exit(1)

    if not os.path.isdir(json_dir):
        print(f"{Colors.RED}Error: JSON directory {json_dir} does not exist.{Colors.ENDC}")
        sys.exit(1)

    for json_file in os.listdir(json_dir):
        if json_file.endswith('.json'):
            json_path = os.path.join(json_dir, json_file)
            schema_path = os.path.join(schema_dir, f"{os.path.splitext(json_file)[0]}_schema.json")

            if not os.path.exists(schema_path):
                print(f"{Colors.YELLOW}⚠️ Schema not found for {json_file}: {schema_path}{Colors.ENDC}")
                continue

            json_data = load_json(json_path)
            schema_data = load_json(schema_path)

            if json_data and schema_data:
                validate_json_against_schema(json_data, schema_data, json_file)


if __name__ == "__main__":
    main()
