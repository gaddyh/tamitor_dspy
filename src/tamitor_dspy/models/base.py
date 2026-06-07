from typing import Any, Literal
from pydantic import BaseModel, Field

Role = Literal["user", "assistant"]

Behavior = Literal[
    "tool_call",
    "clarify",
    "answer_faq",
    "handoff",
]


class Message(BaseModel):
    role: Role
    content: str


class ToolCall(BaseModel):
    tool_name: str
    args: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_name: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | str

AVAILABLE_TOOLS = [
            "book_appointment",
            "get_active_bookings",
            "reschedule_appointment",
            "cancel_appointment",
            "answer_faq",
        ]