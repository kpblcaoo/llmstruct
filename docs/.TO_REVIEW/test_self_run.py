# test_self_run.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import pytest
from pathlib import Path
from llmstruct.self_run import attach_to_llm_request, filter_struct
from llmstruct.json_selector import filter_json, select_json
from llmstruct.cache import JSONCache

def test_filter_json_init_json(tmp_path):
    """Test filter_json with init.json structure."""
    init_json = {
        "guide": {"description": "Test guide"},
        "principles": [{"name": "Transparency", "description": "Open collaboration"}]
    }
    result = filter_json(init_json, "name", "Transparency")
    assert result == [{"name": "Transparency", "description": "Open collaboration"}]

def test_select_json_partial(tmp_path):
    """Test partial JSON loading."""
    init_json = tmp_path / "init.json"
    data = {
        "principles": [{"name": "Transparency", "description": "Open collaboration"}]
    }
    with open(init_json, "w", encoding="utf-8") as f:
        json.dump(data, f)
    
    result = select_json(str(init_json), "name", "Transparency", partial=True)
    assert result == [{"name": "Transparency", "description": "Open collaboration"}]

def test_cache_json(tmp_path):
    """Test JSON caching."""
    cache = JSONCache(str(tmp_path / "cache.db"))
    init_json = tmp_path / "init.json"
    data = {"guide": {"description": "Test guide"}}
    with open(init_json, "w", encoding="utf-8") as f:
        json.dump(data, f)
    
    cache.cache_json(str(init_json), "init.json", summary="Test init", tags=["init"])
    metadata = cache.get_metadata("init.json")
    assert metadata["summary"] == "Test init"
    assert cache.get_full_json("init.json") == data
    cache.close()

def test_attach_to_llm_request_init_json(tmp_path):
    """Test attach_to_llm_request with init.json and cache."""
    cache = JSONCache(str(tmp_path / "cache.db"))
    init_json = tmp_path / "init.json"
    data = {
        "version": "0.1.0",
        "guide": {"description": "LLMstruct guide"},
        "principles": [{"name": "Transparency", "description": "Open collaboration"}]
    }
    with open(init_json, "w", encoding="utf-8") as f:
        json.dump(data, f)
    
    prompt = "Review CLI"
    result = attach_to_llm_request(str(init_json), prompt, cache=cache)
    assert "Context:" in result
    assert '"guide": {"description": "LLMstruct guide"}' in result
    assert '"selected": [{"name": "Transparency"' in result
    cache.close()

def test_attach_to_llm_request_missing_file(tmp_path):
    """Test attach_to_llm_request with missing file."""
    prompt = "Review project"
    result = attach_to_llm_request(str(tmp_path / "missing.json"), prompt)
    assert result == prompt