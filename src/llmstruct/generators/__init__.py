"""Generator modules for creating LLMStruct JSON outputs from parsed code data."""

from .json_generator import generate_json
from .go_json_generator import generate_go_json

__all__ = ["generate_json", "generate_go_json"]
