import tempfile
from pathlib import Path
import pytest

from llmstruct.generators.json_generator import generate_json

pytestmark = pytest.mark.unit


def _write_sample_code(tmp_path: Path):
    sample = """\n\"\"\"Sample module\"\"\"\n\n
def hello():\n    return 1\n\nclass Greeter:\n    def greet(self):\n        return \"hi\"\n"""
    f = tmp_path / "mod.py"
    f.write_text(sample)
    return f


def test_json_generator_adds_tags(tmp_path):
    _write_sample_code(tmp_path)

    result = generate_json(
        root_dir=str(tmp_path),
        include_patterns=["*.py"],
        exclude_patterns=[],
        gitignore_patterns=[],
        include_ranges=False,
        include_hashes=False,
        goals=[],
        exclude_dirs=[],
    )

    module = result["modules"][0]
    assert "module" in module["tags"]
    assert {"function", "public"}.issubset(set(module["functions"][0]["tags"]))
    assert {"class", "public"}.issubset(set(module["classes"][0]["tags"])) 