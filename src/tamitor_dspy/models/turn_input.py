from typing import Any
from pydantic import BaseModel
from .base import AVAILABLE_TOOLS, Message, ToolResult

class TurnInput(BaseModel):
    history: list[Message]
    user_message: str
    tool_results: list[ToolResult]
    context: dict[str, Any]
    available_tools: list = AVAILABLE_TOOLS