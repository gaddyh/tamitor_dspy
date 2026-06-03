from itertools import combinations
from typing import Any, Literal
from pydantic import BaseModel, Field


BehaviorType = Literal[
    "tool_call",
    "clarify",
]


class ToolSpec(BaseModel):
    name: str
    required_args: list[str]
    optional_args: list[str] = Field(default_factory=list)


class ScenarioSpec(BaseModel):
    id: str
    tool_name: str
    scenario_type: Literal["complete_tool_call", "missing_args"]
    expected_behavior: BehaviorType

    provided_args: dict[str, Any]
    missing_args: list[str]

    expected_tool: str | None
    forbidden_tools: list[str] = Field(default_factory=list)

    notes: str


def generate_tool_arg_scenarios(
    tool_registry: list[ToolSpec],
    *,
    max_missing_args: int = 2,
    include_complete: bool = True,
) -> list[ScenarioSpec]:
    """
    Generate one structured scenario per tool behavior boundary.

    For each tool:
    - one complete tool-call scenario
    - one scenario for each missing required arg
    - optional scenarios for pairs/triples of missing required args

    This does not generate user messages.
    It only defines the expected behavior space.
    """

    scenarios: list[ScenarioSpec] = []

    for tool in tool_registry:
        required_args = tool.required_args

        sample_args = {
            arg: f"<{arg}>"
            for arg in required_args
        }

        if include_complete:
            scenarios.append(
                ScenarioSpec(
                    id=f"{tool.name}__complete",
                    tool_name=tool.name,
                    scenario_type="complete_tool_call",
                    expected_behavior="tool_call",
                    provided_args=sample_args,
                    missing_args=[],
                    expected_tool=tool.name,
                    forbidden_tools=[],
                    notes=(
                        f"All required args for {tool.name} are present. "
                        f"The agent should call {tool.name}."
                    ),
                )
            )

        max_k = min(max_missing_args, len(required_args))

        for k in range(1, max_k + 1):
            for missing in combinations(required_args, k):
                missing = list(missing)

                provided_args = {
                    arg: f"<{arg}>"
                    for arg in required_args
                    if arg not in missing
                }

                scenarios.append(
                    ScenarioSpec(
                        id=f"{tool.name}__missing__{'__'.join(missing)}",
                        tool_name=tool.name,
                        scenario_type="missing_args",
                        expected_behavior="clarify",
                        provided_args=provided_args,
                        missing_args=missing,
                        expected_tool=None,
                        forbidden_tools=[tool.name],
                        notes=(
                            f"{tool.name} intent exists, but missing required args: "
                            f"{', '.join(missing)}. The agent should clarify, "
                            f"not call {tool.name}."
                        ),
                    )
                )

    return scenarios