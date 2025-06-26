import pytest

from llmstruct.core.tag_inference import infer_tags


@pytest.mark.unit
def test_infer_public_function_tags():
    code = "def hello():\n    return 'hi'"
    tags = infer_tags(code=code, entity_type="function", entity_name="hello")
    assert tags == ["function", "public"]


@pytest.mark.unit
def test_infer_private_async_generator_method_tags():
    code = "async def _worker():\n    yield 1"
    tags = infer_tags(code=code, entity_type="method", entity_name="_worker")
    expected = {"method", "private", "async", "generator"}
    assert set(tags) == expected


@pytest.mark.unit
def test_infer_class_decorator_tags():
    code = """class MyClass:\n    @staticmethod\n    def util():\n        pass"""
    tags = infer_tags(code=code, entity_type="class", entity_name="MyClass")
    assert set(tags) == {"class", "public", "static"} 