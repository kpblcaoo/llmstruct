import json
from jsonschema import validate, ValidationError

def validate_struct_json(json_path: str, schema_path: str) -> bool:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            struct = json.load(f)
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        validate(instance=struct, schema=schema)
        print("JSON is valid.")
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python json_validator.py <struct.json> <schema.json>")
        sys.exit(1)
    validate_struct_json(sys.argv[1], sys.argv[2])