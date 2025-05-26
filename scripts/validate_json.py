#!/usr/bin/env python3
"""
JSON Validation Script
Validates JSON files against their respective schemas.
"""

import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator


def load_json(file_path):
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        return None


def validate_json(file_path, schema_path):
    """Validate a JSON file against a schema."""
    json_data = load_json(file_path)
    schema_data = load_json(schema_path)

    if json_data is None or schema_data is None:
        return False

    try:
        # Create resolver for schema references
        schema_dir = Path(schema_path).parent
        validator = Draft7Validator(schema_data)
        
        validator.validate(json_data)
        print(f"Success: {file_path} is valid.")
        return True
    except ValidationError as e:
        print(f"Validation Error in {file_path}:")
        print(f"  Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        print(f"  Message: {e.message}")
        return False
    except Exception as e:
        print(f"Unexpected error during validation: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: validate_json.py <json_file> <schema_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    schema_file = sys.argv[2]

    if not validate_json(json_file, schema_file):
        sys.exit(1)
    sys.exit(0)