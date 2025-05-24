import json
import logging
from pathlib import Path
from jsonschema import validate, ValidationError
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_struct_json(json_path: str, schema_path: str) -> bool:
    """Validate a single JSON file against a schema."""
    try:
        json_file = Path(json_path)
        schema_file = Path(schema_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return False
        if not schema_file.exists():
            logging.error(f"Schema file not found: {schema_path}")
            return False

        with open(json_file, "r", encoding="utf-8") as f:
            struct = json.load(f)
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        validate(instance=struct, schema=schema)
        logging.info(f"JSON is valid: {json_path}")
        return True
    except ValidationError as e:
        logging.error(f"Validation error in {json_path}: {e.message}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {json_path}: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error in {json_path}: {str(e)}")
        return False

def validate_directory(directory: str, schema_path: str, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None) -> bool:
    """Validate all JSON files in a directory against a schema."""
    include_patterns = include_patterns or ["*.json"]
    exclude_patterns = exclude_patterns or []
    valid = True
    
    for json_file in Path(directory).rglob("*.json"):
        if any(json_file.match(p) for p in include_patterns) and not any(json_file.match(ep) for ep in exclude_patterns):
            if not validate_struct_json(str(json_file), schema_path):
                valid = False
    
    return valid

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        logging.error("Usage: python json_validator.py <path> <schema.json> [--include <pattern>] [--exclude <pattern>]")
        sys.exit(1)
    
    path, schema_path = sys.argv[1], sys.argv[2]
    include_patterns = [sys.argv[sys.argv.index("--include") + 1]] if "--include" in sys.argv else None
    exclude_patterns = [sys.argv[sys.argv.index("--exclude") + 1]] if "--exclude" in sys.argv else None
    
    if Path(path).is_dir():
        success = validate_directory(path, schema_path, include_patterns, exclude_patterns)
    else:
        success = validate_struct_json(path, schema_path)
    
    sys.exit(0 if success else 1)
