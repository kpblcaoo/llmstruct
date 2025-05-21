import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def filter_json(data: Dict[str, Any], filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter JSON data by key-value pair and select fields."""
    filtered = []
    items = data.get("ideas", []) or data.get("tasks", []) or data.get("docs", []) or data.get("prs", []) or data.get("conflicts", [])
    
    for item in items:
        if item.get(filter_key) == filter_value:
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
            data = json
