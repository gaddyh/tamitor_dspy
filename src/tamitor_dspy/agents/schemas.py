from typing import Any
from pydantic import BaseModel

class AgentRun(BaseModel):
    response: str
    called_tools: list[dict[str, Any]]
    raw_trajectory: dict[str, Any]
