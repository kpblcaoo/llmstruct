import importlib
import pytest
from pathlib import Path

esprima_spec = importlib.util.find_spec("esprima")

pytestmark = pytest.mark.unit


@pytest.mark.skipif(esprima_spec is None, reason="esprima not installed")
def test_javascript_parser_tags(tmp_path):
    """Ensure JavaScript parser adds default tags."""
    # prepare simple JS file
    js_code = """
    // test module
    function Hello() {
        return 42;
    }
    """
    js_file = tmp_path / "hello.js"
    js_file.write_text(js_code)

    from llmstruct.parsers.javascript_parser import JavaScriptParser

    parser = JavaScriptParser()
    result = parser.parse_module(str(js_file), str(tmp_path), include_ranges=False, include_hashes=False)

    assert "tags" in result and "module" in result["tags"]

    func_tags = result["functions"][0]["tags"]
    assert set(func_tags) == {"function", "public"} 