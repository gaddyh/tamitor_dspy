from pydantic import BaseModel
from typing import Any

from .base import Behavior
from .turn_input import TurnInput

class DatasetRow(BaseModel):
    id: str
    input: TurnInput

    expected_behavior: Behavior
    expected_tool: str | None
    expected_args: dict[str, Any]

    expected_missing_fields: list[str]

    forbidden_tools: list[str]
    forbidden_args: list[str]

    notes: str = ""

