# Восстановлено из ARCHIVE/to_review/self_run.py 

# self_run.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import logging
from pathlib import Path
from typing import Any, Optional
from .json_selector import filter_json, select_json
from .cache import JSONCache

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def filter_struct(struct, prompt: str) -> Any:
    """Filter struct.json or init.json based on prompt keywords. Supports dict or list as root."""
    if isinstance(struct, list):
        # Фильтрация списка по ключевым словам в prompt (ищем dict-элементы с
        # path/summary)
        keywords = prompt.lower().split()
        filtered = [
            item
            for item in struct
            if isinstance(item, dict)
            and any(
                k in str(item.get("path", "")).lower()
                or k in str(item.get("summary", "")).lower()
                for k in keywords
            )
        ]
        return filtered
    elif isinstance(struct, dict):
        if "guide" in struct:
            filtered = {
                "metadata": struct.get(
                    "metadata",
                    {
                        "project_name": "llmstruct",
                        "version": struct.get("version", "0.0.0"),
                    },
                ),
                "guide": struct.get("guide", {}),
            }
            keywords = prompt.lower().split()
            if "cli" in keywords:
                filtered["principles"] = filter_json(struct, "name", "Transparency")
            return filtered
        filtered = {
            "metadata": struct.get(
                "metadata",
                {"project_name": "unknown", "description": "", "version": "0.0.0"},
            ),
            "modules": [],
        }
        keywords = prompt.lower().split()
        for module in struct.get("modules", []):
            if any(
                k in module.get("path", "").lower()
                or k in module.get("summary", "").lower()
                for k in keywords
            ):
                filtered["modules"].append(module)
        return filtered
    else:
        # Неизвестный тип, возвращаем как есть
        return struct


def attach_to_llm_request(
    context_path: str, prompt: str, cache: Optional[JSONCache] = None
) -> str:
    """Attach filtered JSON to LLM prompt, using cache if available."""
    try:
        context_file = Path(context_path)
        if not context_file.exists():
            logging.error(f"Context file not found: {context_path}")
            return prompt

        # Check cache first
        if cache:
            metadata = cache.get_metadata(context_file.name)
            if metadata and "cli" in prompt.lower():
                struct = cache.get_full_json(context_file.name)
                if struct:
                    logging.info(f"Loaded {context_path} from cache")
                else:
                    struct = select_json(context_path, "category", "cli", partial=True)
            else:
                struct = select_json(context_path, "category", "cli", partial=True)
        else:
            struct = select_json(context_path, "category", "cli", partial=True)

        filtered_struct = filter_struct(struct, prompt)
        selected_data = (
            filter_json(struct, "category", "cli") if "cli" in prompt.lower() else []
        )
        context = {"struct": filtered_struct, "selected": selected_data}
        # Cache result if cache is enabled
        if cache and context_file.exists():
            cache.cache_json(
                context_path, context_file.name, summary=prompt[:50], tags=["cli"]
            )
        return f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {context_path}: {e}")
        return prompt
    except Exception as e:
        logging.error(f"Error processing {context_path}: {e}")
        return prompt 