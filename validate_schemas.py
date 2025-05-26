#!/usr/bin/env python3
"""
JSON Schema Validation Script for llmstruct
Validates all enhanced JSON files against their appropriate schemas.
Part of TSK-130 implementation.
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
        validate(
            instance=json_data,
            schema=schema_data,
            format_checker=Draft7Validator.FORMAT_CHECKER)
        print(f"{Colors.GREEN}✅ {file_name}: Valid{Colors.ENDC}")
        return True
    except ValidationError as e:
        print(f"{Colors.RED}❌ {file_name}: Validation Error{Colors.ENDC}")
        print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        print(f"   Error: {e.message}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ {file_name}: Unexpected error: {e}{Colors.ENDC}")
        return False


def main():
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 llmstruct JSON Schema Validation{Colors.ENDC}")
    print(f"{Colors.BLUE}Part of TSK-130: Validate JSON schema compliance{Colors.ENDC}")
    print()

    # Define file-to-schema mappings
    validations = [
        # Core project files
        {
            "file": "struct.json",
            "schema": "schema/llmstruct_schema_simplified.json",
            "description": "Main project structure"
        },
        {
            "file": "data/tasks.json",
            "schema": "schema/core_simplified.json",
            "description": "Task management"
        },

        # Enhanced files (new)
        {
            "file": "data/init_enhanced.json",
            "schema": "schema/core_simplified.json",
            "description": "Enhanced context orchestration"
        },
        {
            "file": "data/cli_enhanced.json",
            "schema": "schema/cli_simplified.json",
            "description": "Enhanced CLI automation"
        },
        {
            "file": "data/cli_queue_enhanced.json",
            "schema": "schema/cli_queue.json",
            "description": "Enhanced workflow system"
        },

        # Standard data files
        {
            "file": "data/cli.json",
            "schema": "schema/cli_simplified.json",
            "description": "CLI configuration"
        },
        {
            "file": "data/cli_queue.json",
            "schema": "schema/cli_queue.json",
            "description": "CLI queue system"
        },
        {
            "file": "data/artifacts_index.json",
            "schema": "schema/artifacts_simplified.json",
            "description": "Artifacts index"
        },
        {
            "file": "data/insights.json",
            "schema": "schema/insights_simplified.json",
            "description": "Project insights"
        },

        # New project management files
        {
            "file": "data/ideas.json",
            "schema": "schema/core_simplified.json",
            "description": "Project ideas"
        },
        {
            "file": "data/prs.json",
            "schema": "schema/core_simplified.json",
            "description": "Pull request tracking"
        },
        {
            "file": "data/ideas_cache.json",
            "schema": "schema/core_simplified.json",
            "description": "Ideas cache"
        },
        # Session management files (NEW)
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
    print(f"{Colors.BOLD}📊 Validation Summary{Colors.ENDC}")
    print(f"Valid files: {Colors.GREEN}{valid_count}/{total_count}{Colors.ENDC}")

    if errors:
        print(f"{Colors.RED}❌ Errors found:{Colors.ENDC}")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print(f"{Colors.GREEN}🎉 All JSON files are valid!{Colors.ENDC}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
