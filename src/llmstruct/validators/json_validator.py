import json
import logging
from pathlib import Path
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_struct_json(json_path: str, schema_path: str) -> bool:
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
        logging.error(f"Validation error: {e.message}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        logging.error("Usage: python json_validator.py <struct.json> <schema.json>")
        sys.exit(1)
    success = validate_struct_json(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)