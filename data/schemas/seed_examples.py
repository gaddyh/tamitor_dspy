
"""
Seed examples for testing the TamiTorTurnDecision agent.
"""
from src.tamitor_dspy.models.labeled import DatasetRow
from src.tamitor_dspy.models.turn_input import TurnInput
from src.tamitor_dspy.models.base import AVAILABLE_TOOLS

full_details_example = DatasetRow(
    id="book_complete_001",
    input=TurnInput(
        history=[],
        user_message="I'd like a haircut tomorrow at 3pm",
        tool_results=[],
        context={
            "current_date": "2026-06-07",
            "user_name": "Gadi",
        },
        available_tools=AVAILABLE_TOOLS,
    ),
    expected_behavior="tool_call",
    expected_tool="book_appointment",
    expected_args={
        "service": "haircut",
        "date": "2026-06-08",
        "time": "15:00",
        "customer_name": "Gadi",
    },
    expected_missing_fields=[],
    forbidden_tools=[],
    forbidden_args=[],
    notes="",
)


missing_time_example = DatasetRow(
    id="book_missing_time_001",
    input=TurnInput(
        history=[],
        user_message="I'd like a haircut tomorrow",
        tool_results=[],
        context={
            "current_date": "2026-06-07",
            "user_name": "Gadi",
        },
        available_tools=AVAILABLE_TOOLS,
    ),
    expected_behavior="clarify",
    expected_tool=None,
    expected_args={},
    expected_missing_fields=["time"],
    forbidden_tools=["book_appointment"],
    forbidden_args=["time"],
)