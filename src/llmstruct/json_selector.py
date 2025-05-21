# json_selector.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def filter_json(data: Dict[str, Any], filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter JSON data by key-value pair and select fields."""
    filtered = []
    items = data.get("ideas", []) or data.get("tasks", []) or data.get("docs", []) or data.get("prs", []) or data.get("conflicts", []) or data.get("principles", []) or data.get("guide", [])
    
    for item in items:
        if isinstance(item, dict) and item.get(filter_key) == filter_value:
            if fields:
                filtered.append({k: item[k] for k in fields if k in item})
            else:
                filtered.append(item)
    
    return filtered

def select_json(json_path: str, filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Load and filter JSON file."""
    try:
        json_file = Path(json_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return []
        
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return filter_json(data, filter_key, filter_value, fields)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {json_path}: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error in {json_path}: {e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter JSON data by key-value pair")
    parser.add_argument("json_path", help="Path to JSON file")
    parser.add_argument("--filter-key", required=True, help="Key to filter by")
    parser.add_argument("--filter-value", required=True, help="Value to filter by")
    parser.add_argument("--fields", nargs="*", help="Fields to include in output")
    args = parser.parse_args()
    
    result = select_json(args.json_path, args.filter_key, args.filter_value, args.fields)
    print(json.dumps(result, indent=2))