# self_run.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from .json_selector import filter_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def filter_struct(struct: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Filter struct.json or init.json based on prompt keywords."""
    # Handle init.json structure
    if "guide" in struct:
        filtered = {
            "metadata": struct.get("metadata", {"project_name": "llmstruct", "version": struct.get("version", "0.0.0")}),
            "guide": struct.get("guide", {})
        }
        keywords = prompt.lower().split()
        if "cli" in keywords:
            filtered["principles"] = filter_json(struct, "name", "Transparency")
        return filtered
    # Handle struct.json structure
    filtered = {"metadata": struct.get("metadata", {"project_name": "unknown", "description": "", "version": "0.0.0"}), "modules": []}
    keywords = prompt.lower().split()
    
    for module in struct.get("modules", []):
        if any(k in module.get("path", "").lower() or k in module.get("summary", "").lower() for k in keywords):
            filtered["modules"].append(module)
    
    return filtered

def attach_to_llm_request(context_path: str, prompt: str) -> str:
    """Attach filtered JSON to LLM prompt."""
    try:
        context_file = Path(context_path)
        if not context_file.exists():
            logging.error(f"Context file not found: {context_path}")
            return prompt
        
        with open(context_file, "r", encoding="utf-8") as f:
            struct = json.load(f)
        
        filtered_struct = filter_struct(struct, prompt)
        # Use json_selector for CLI-related data
        selected_data = filter_json(struct, "category", "cli") if "cli" in prompt.lower() else []
        context = {
            "struct": filtered_struct,
            "selected": selected_data
        }
        return f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {context_path}: {e}")
        return prompt
    except Exception as e:
        logging.error(f"Error processing {context_path}: {e}")
        return prompt