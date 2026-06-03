from typing import Any, Literal
from pydantic import BaseModel, Field


ExpectedBehavior = Literal[
    "tool_call",
    "clarify",
    "answer_only",
]


class DatasetExample(BaseModel):
    id: str
    category: str

    request: str
    context: str = ""

    expected_behavior: ExpectedBehavior

    expected_tool: str | None = None
    expected_args: dict[str, Any] = Field(default_factory=dict)

    missing_args: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)

    notes: str = ""

