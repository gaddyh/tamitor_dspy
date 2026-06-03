# scripts/generate_seed_examples.py

import dspy

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

    generator = ValidatedScenarioMessageGenerator(max_attempts=3)

    examples = []

    for scenario in scenarios:
        example = generator(scenario)
        examples.append(example)
        print(example.model_dump_json(ensure_ascii=False))

    return examples


if __name__ == "__main__":
    main()