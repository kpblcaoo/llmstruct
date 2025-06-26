import pytest

from llmstruct.parsers.go_converter import convert_to_llmstruct_format


@pytest.mark.unit
def test_go_converter_adds_tags():
    analysis = {
        "files": [
            {
                "path": "pkg/example/util.go",
                "package": "example",
                "functions": [
                    {"name": "Hello", "line": 1},
                ],
                "structs": [
                    {"name": "Service", "line": 10, "fields": [], "methods": []},
                ],
                "interfaces": [],
                "imports": [],
            }
        ],
        "all_packages": ["example"],
    }

    result = convert_to_llmstruct_format(analysis)
    module = result["modules"][0]

    # Module tags must include "module"
    assert "module" in module["tags"]

    func_tags = module["functions"][0]["tags"]
    assert set(func_tags) == {"function", "public"}

    class_tags = module["classes"][0]["tags"]
    assert set(class_tags) == {"class", "public"} 