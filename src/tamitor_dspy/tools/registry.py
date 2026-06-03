
from typing import Any

from src.tamitor_dspy.datasets.scenario_spec import ToolSpec

tool_registry = [
    ToolSpec(
        name="book_appointment",
        required_args=["service", "date", "time", "customer_name"],
    ),
    ToolSpec(
        name="reschedule_appointment",
        required_args=["appointment_id", "date", "time"],
    ),
    ToolSpec(
        name="cancel_appointment",
        required_args=["appointment_id"],
    ),
    ToolSpec(
        name="answer_faq",
        required_args=["topic"],
    ),
    ToolSpec(
        name="handoff_to_human",
        required_args=["reason"],
    ),
]


def extract_tool_calls_from_trajectory(trajectory: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Best-effort extractor for DSPy ReAct trajectories.

    You may need to adjust this after inspecting actual trajectory keys.
    """
    calls = []

    for key, value in trajectory.items():
        text = str(value)

        for tool_name in [
            "book_appointment",
            "reschedule_appointment",
            "cancel_appointment",
            "answer_faq",
        ]:
            if tool_name in text:
                calls.append(
                    {
                        "tool_name": tool_name,
                        "raw": text,
                        "trajectory_key": key,
                    }
                )

    return calls