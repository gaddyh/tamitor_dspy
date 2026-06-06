from typing import Any
from pydantic import BaseModel, Field

from src.tamitor_dspy.models.labeled import DatasetRow
from src.tamitor_dspy.models.prediction import PredictionTrace


class EvalResult(BaseModel):
    id: str

    behavior_match: bool
    tool_match: bool
    args_match: bool
    missing_fields_match: bool
    forbidden_tool_used: bool
    forbidden_arg_used: bool

    score: float
    notes: list[str] = Field(default_factory=list)

    trace: PredictionTrace | None = None


def evaluate_prediction(row: DatasetRow, prediction) -> EvalResult:
    notes: list[str] = []

    behavior_match = prediction.result.behavior == row.expected_behavior

    predicted_tool = None
    predicted_args: dict[str, Any] = {}

    if prediction.result.tool_result is not None:
        predicted_tool = prediction.result.tool_result.tool_name
        predicted_args = prediction.result.tool_result.args or {}

    tool_match = predicted_tool == row.expected_tool

    expected_args = row.expected_args or {}
    args_match = all(
        predicted_args.get(k) == v
        for k, v in expected_args.items()
    )

    missing_fields_match = set(prediction.result.missing_fields or []) == set(
        row.expected_missing_fields or []
    )

    forbidden_tool_used = predicted_tool in (row.forbidden_tools or [])

    forbidden_arg_used = any(
        arg in predicted_args and predicted_args[arg] not in [None, ""]
        for arg in (row.forbidden_args or [])
    )

    if not behavior_match:
        notes.append(
            f"behavior mismatch: expected={row.expected_behavior}, got={prediction.result.behavior}"
        )

    if not tool_match:
        notes.append(
            f"tool mismatch: expected={row.expected_tool}, got={predicted_tool}"
        )

    if not args_match:
        notes.append(
            f"args mismatch: expected subset={expected_args}, got={predicted_args}"
        )

    if not missing_fields_match:
        notes.append(
            f"missing fields mismatch: expected={row.expected_missing_fields}, got={prediction.result.missing_fields}"
        )

    if forbidden_tool_used:
        notes.append(f"forbidden tool used: {predicted_tool}")

    if forbidden_arg_used:
        notes.append(
            f"forbidden arg used: forbidden={row.forbidden_args}, got={predicted_args}"
        )

    score_parts = [
        behavior_match,
        tool_match,
        args_match,
        missing_fields_match,
        not forbidden_tool_used,
        not forbidden_arg_used,
    ]

    score = sum(score_parts) / len(score_parts)

    return EvalResult(
        id=row.id,
        behavior_match=behavior_match,
        tool_match=tool_match,
        args_match=args_match,
        missing_fields_match=missing_fields_match,
        forbidden_tool_used=forbidden_tool_used,
        forbidden_arg_used=forbidden_arg_used,
        score=score,
        notes=notes,
    )