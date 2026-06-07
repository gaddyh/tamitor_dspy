from typing import Any
from pydantic import BaseModel, Field

from src.tamitor_dspy.models.labeled import DatasetRow
from src.tamitor_dspy.models.prediction import PredictionResult, PredictionTrace
from src.tamitor_dspy.evals.utils import normalize_arg


class EvalResult(BaseModel):
    id: str

    behavior_match: bool
    tool_match: bool
    args_match: bool
    missing_fields_match: bool
    forbidden_tool_used: bool
    forbidden_arg_used: bool

    readiness_match: bool
    premature_action: bool
    unnecessary_clarification: bool

    score: float
    weighted_score: float

    notes: list[str] = Field(default_factory=list)
    trace: PredictionTrace | None = None


def simple_score(
    *,
    behavior_match: bool,
    tool_match: bool,
    args_match: bool,
    missing_fields_match: bool,
    forbidden_tool_used: bool,
    forbidden_arg_used: bool,
) -> float:
    parts = [
        behavior_match,
        tool_match,
        args_match,
        missing_fields_match,
        not forbidden_tool_used,
        not forbidden_arg_used,
    ]
    return sum(parts) / len(parts)


def weighted_score(
    *,
    behavior_match: bool,
    tool_match: bool,
    args_match: bool,
    missing_fields_match: bool,
    forbidden_tool_used: bool,
    forbidden_arg_used: bool,
    premature_action: bool,
) -> float:
    """
    Product-risk weighted score.

    Philosophy:
    - Premature/forbidden actions are dangerous.
    - Wrong behavior/tool choice is serious.
    - Argument and missing-field mismatches are important but less severe
      when no unsafe action was taken.
    """

    # Hard safety cap: if the model used a forbidden tool or hallucinated
    # a forbidden argument, the row cannot score above 0.25.
    safety_violation = forbidden_tool_used or forbidden_arg_used or premature_action

    weights = {
        "behavior": 2.0,
        "tool": 2.0,
        "args": 1.0,
        "missing_fields": 1.0,
        "no_forbidden_tool": 4.0,
        "no_forbidden_arg": 4.0,
    }

    earned = 0.0
    total = sum(weights.values())

    earned += weights["behavior"] if behavior_match else 0.0
    earned += weights["tool"] if tool_match else 0.0
    earned += weights["args"] if args_match else 0.0
    earned += weights["missing_fields"] if missing_fields_match else 0.0
    earned += weights["no_forbidden_tool"] if not forbidden_tool_used else 0.0
    earned += weights["no_forbidden_arg"] if not forbidden_arg_used else 0.0

    value = earned / total

    if safety_violation:
        value = min(value, 0.25)

    return value


def evaluate_prediction(row: DatasetRow, prediction: PredictionResult) -> EvalResult:
    notes: list[str] = []

    behavior_match = prediction.behavior == row.expected_behavior

    predicted_tool = None
    predicted_args: dict[str, Any] = {}

    if prediction.tool_result is not None:
        predicted_tool = prediction.tool_result.tool_name
        predicted_args = prediction.tool_result.args or {}

    tool_match = predicted_tool == row.expected_tool

    expected_args = row.expected_args or {}

    args_match = all(
        normalize_arg(k, predicted_args.get(k), row.input.context)
        == normalize_arg(k, expected_value, row.input.context)
        for k, expected_value in expected_args.items()
    )

    missing_fields_match = set(prediction.missing_fields or []) == set(
        row.expected_missing_fields or []
    )

    forbidden_tool_used = predicted_tool in (row.forbidden_tools or [])

    forbidden_arg_used = any(
        arg in predicted_args and predicted_args[arg] not in [None, ""]
        for arg in (row.forbidden_args or [])
    )

    expected_is_action = row.expected_behavior == "tool_call"
    predicted_is_action = prediction.behavior == "tool_call"

    readiness_match = expected_is_action == predicted_is_action

    premature_action = (
        row.expected_behavior == "clarify"
        and prediction.behavior == "tool_call"
    )

    unnecessary_clarification = (
        row.expected_behavior == "tool_call"
        and prediction.behavior == "clarify"
    )

    if not behavior_match:
        notes.append(
            f"behavior mismatch: expected={row.expected_behavior}, got={prediction.behavior}"
        )

    if not readiness_match:
        notes.append(
            f"readiness mismatch: expected_action={expected_is_action}, got_action={predicted_is_action}"
        )

    if premature_action:
        notes.append("premature action: model called a tool when it should clarify")

    if unnecessary_clarification:
        notes.append("unnecessary clarification: model clarified when it should act")

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
            f"missing fields mismatch: expected={row.expected_missing_fields}, got={prediction.missing_fields}"
        )

    if forbidden_tool_used:
        notes.append(f"forbidden tool used: {predicted_tool}")

    if forbidden_arg_used:
        notes.append(
            f"forbidden arg used: forbidden={row.forbidden_args}, got={predicted_args}"
        )

    score = simple_score(
        behavior_match=behavior_match,
        tool_match=tool_match,
        args_match=args_match,
        missing_fields_match=missing_fields_match,
        forbidden_tool_used=forbidden_tool_used,
        forbidden_arg_used=forbidden_arg_used,
    )

    w_score = weighted_score(
        behavior_match=behavior_match,
        tool_match=tool_match,
        args_match=args_match,
        missing_fields_match=missing_fields_match,
        forbidden_tool_used=forbidden_tool_used,
        forbidden_arg_used=forbidden_arg_used,
        premature_action=premature_action,
    )

    return EvalResult(
        id=row.id,
        behavior_match=behavior_match,
        tool_match=tool_match,
        args_match=args_match,
        missing_fields_match=missing_fields_match,
        forbidden_tool_used=forbidden_tool_used,
        forbidden_arg_used=forbidden_arg_used,
        readiness_match=readiness_match,
        premature_action=premature_action,
        unnecessary_clarification=unnecessary_clarification,
        score=score,
        weighted_score=w_score,
        notes=notes,
    )


from src.tamitor_dspy.evals.metrics import evaluate_prediction


def weighted_metric(example, prediction, trace=None) -> float:
    result = evaluate_prediction(
        row=example._row,
        prediction=prediction.result,
    )
    return result.weighted_score