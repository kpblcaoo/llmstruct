#!/usr/bin/env python3
"""
Session Schema Validation Script for llmstruct
Validates session management JSON files against their schemas.
Focused validation for session system only.
"""

import json
import sys
from jsonschema import validate, ValidationError, Draft7Validator

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
        validator = Draft7Validator(schema_data)
        errors = list(validator.iter_errors(json_data))
        
        if not errors:
            print(f"{Colors.GREEN}✅ {file_name}: Valid{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}❌ {file_name}: Validation Error(s){Colors.ENDC}")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   Path: {' -> '.join(str(p) for p in error.absolute_path)}")
                print(f"   Error: {error.message}")
            if len(errors) > 3:
                print(f"   ... and {len(errors) - 3} more errors")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ {file_name}: Unexpected error: {e}{Colors.ENDC}")
        return False

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 Session Management Schema Validation{Colors.ENDC}")
    print(f"{Colors.BLUE}Validates session management files only{Colors.ENDC}")
    print()

    # Define session file validations only
    validations = [
        {
            "file": "data/sessions/ai_sessions.json",
            "schema": "schema/session_ai_sessions.json",
            "description": "AI session metadata and knowledge cache"
        },
        {
            "file": "data/sessions/current_session.json",
            "schema": "schema/session_current_session.json",
            "description": "Current session state"
        },
        {
            "file": "data/sessions/worklog.json",
            "schema": "schema/session_worklog.json",
            "description": "Session worklog/events log"
        }
    ]

    valid_count = 0
    total_count = 0
    errors = []

    for validation in validations:
        file_path = validation["file"]
        schema_path = validation["schema"]
        description = validation["description"]

        print(f"{Colors.YELLOW}Validating: {description}{Colors.ENDC}")

        # Load JSON file
        json_data = load_json(file_path)
        if json_data is None:
            errors.append(f"Failed to load {file_path}")
            total_count += 1
            continue

        # Load schema
        schema_data = load_json(schema_path)
        if schema_data is None:
            errors.append(f"Failed to load schema {schema_path}")
            total_count += 1
            continue

        # Validate
        if validate_json_against_schema(json_data, schema_data, file_path):
            valid_count += 1
        else:
            errors.append(f"Validation failed for {file_path}")

        total_count += 1
        print()

    # Summary
    print(f"{Colors.BOLD}📊 Session Validation Summary{Colors.ENDC}")
    print(f"Valid session files: {Colors.GREEN}{valid_count}/{total_count}{Colors.ENDC}")

    if errors:
        print(f"{Colors.RED}❌ Session errors found:{Colors.ENDC}")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print(f"{Colors.GREEN}🎉 All session files are valid!{Colors.ENDC}")
        print(f"{Colors.BLUE}Session management system is ready for production.{Colors.ENDC}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
