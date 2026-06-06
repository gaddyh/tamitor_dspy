# scripts/generate_seed_examples.py

import dspy
from pathlib import Path

from src.tamitor_dspy.tools.registry import tool_registry
from src.tamitor_dspy.datasets.scenario_spec import generate_tool_arg_scenarios
from src.tamitor_dspy.datasets.generate_messages import ValidatedScenarioMessageGenerator


def main():
    lm = dspy.LM(
        "openai/gpt-4o-mini",
        temperature=0.8,
    )
    dspy.configure(lm=lm)

    scenarios = generate_tool_arg_scenarios(
        tool_registry,
        max_missing_args=2,
    )

    current_path = Path(__file__).parent
    open(current_path / "scenarios.jsonl", "w").write("\n".join([scenario.model_dump_json() for scenario in scenarios]))
    return scenarios


if __name__ == "__main__":
    scenarios = main()
    print(scenarios)