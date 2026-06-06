

from typing import Any
from data.schemas.seed_examples import DatasetExample
from src.tamitor_dspy.agents.schemas import AgentRun
from src.tamitor_dspy.evals.metrics import tool_selection_score, forbidden_tool_violation, clarification_score
from src.tamitor_dspy.tools.registry import extract_tool_calls_from_trajectory

def run_agent_on_example(agent, example: DatasetExample) -> AgentRun:
    result = agent(
        request=example.user_message,
        context=example.context,
    )

    called_tools = extract_tool_calls_from_trajectory(result.trajectory)

    return AgentRun(
        response=result.response,
        called_tools=called_tools,
        raw_trajectory=result.trajectory,
    )



def evaluate_example(agent, example: DatasetExample) -> dict[str, Any]:
    run = run_agent_on_example(agent, example)

    return {
        "id": example.id,
        "user_message": example.user_message,
        "context": example.context,
        "response": run.response,
        "called_tools": run.called_tools,

        "tool_selection_score": tool_selection_score(example, run),
        "forbidden_tool_violation": forbidden_tool_violation(example, run),
        "clarification_score": clarification_score(example, run),

        "expected_behavior": example.expected_behavior,
        "expected_tool": example.expected_tool,
        "missing_args": example.expected_missing_fields,
        "notes": example.notes,
    }