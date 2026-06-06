from pydantic import BaseModel, Field
from datetime import datetime

from .base import Behavior, ToolResult

class PredictionResult(BaseModel):
    behavior: Behavior

    tool_result: ToolResult | None = None

    message: str = Field(
        default="",
        description="User-facing response when behavior is clarify, answer_faq, or handoff.",
    )

    missing_fields: list[str] = Field(
        default_factory=list,
        description="Fields the assistant believes are required but missing.",
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class PredictionTrace(BaseModel):
    started_at: datetime
    finished_at: datetime
    duration_ms: float