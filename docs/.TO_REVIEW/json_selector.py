# json_selector.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import argparse
import ijson
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def filter_json(data: Dict[str, Any], filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter JSON data by key-value pair and select fields."""
    filtered = []
    items = data.get("ideas", []) or data.get("tasks", []) or data.get("docs", []) or data.get("prs", []) or data.get("conflicts", []) or data.get("principles", []) or data.get("guide", []) or data.get("modules", [])
    
    for item in items:
        if isinstance(item, dict) and item.get(filter_key) == filter_value:
            if fields:
                filtered.append({k: item[k] for k in fields if k in item})
            else:
                filtered.append(item)
    
    return filtered

def select_json(json_path: str, filter_key: str, filter_value: str, fields: Optional[List[str]] = None, partial: bool = False) -> List[Dict[str, Any]]:
    """Load and filter JSON file, optionally parsing partially."""
    try:
        json_file = Path(json_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return []
        
        if partial:
            filtered = []
            with open(json_file, "r", encoding="utf-8") as f:
                # Parse specific arrays incrementally
                for prefix in ["ideas.item", "tasks.item", "docs.item", "prs.item", "conflicts.item", "principles.item", "guide.item", "modules.item"]:
                    f.seek(0)  # Reset file pointer
                    parser = ijson.parse(f)
                    current_item = {}
                    path = []
                    for prefix, event, value in parser:
                        if prefix.startswith(prefix) and event == "map_key":
                            path.append(value)
                        elif prefix.startswith(prefix) and event == "end_map":
                            if current_item.get(filter_key) == filter_value:
                                if fields:
                                    filtered.append({k: current_item[k] for k in fields if k in current_item})
                                else:
                                    filtered.append(current_item)
                            current_item = {}
                            path = []
                        elif prefix.startswith(prefix) and event in ("string", "number", "boolean", "null"):
                            if path:
                                current_item[path[-1]] = value
            return filtered
        else:
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
    parser.add_argument("--partial", action="store_true", help="Parse JSON partially")
    args = parser.parse_args()
    
    result = select_json(args.json_path, args.filter_key, args.filter_value, args.fields, args.partial)
    print(json.dumps(result, indent=2))