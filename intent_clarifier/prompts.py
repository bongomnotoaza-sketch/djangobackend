import json
from pathlib import Path

from .system_prompt import SYSTEM_PROMPT

_EXAMPLES_PATH = Path(__file__).parent / "examples.json"

with open(_EXAMPLES_PATH, "r") as f:
    FEW_SHOT = json.load(f)