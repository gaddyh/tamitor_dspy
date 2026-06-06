import dspy
from typing import Any
from rich.console import Console
from rich.table import Table
from rich import box

from data.schemas.seed_examples import DatasetExample
from src.tamitor_dspy.tools.impl import (
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
    answer_faq,
)
from src.tamitor_dspy.agents.signatures import TamiTorReAct
from src.tamitor_dspy.evals.evaluator import evaluate_example


lm = dspy.LM("openai/gpt-5.4-mini")
dspy.configure(lm=lm)


agent = dspy.ReAct(
    TamiTorReAct,
    tools=[
        book_appointment,
        reschedule_appointment,
        cancel_appointment,
        answer_faq,
    ],
)


def run_baseline(agent, examples: list[DatasetExample]) -> list[dict[str, Any]]:
    results = []

    for example in examples:
        result = evaluate_example(agent, example)
        results.append(result)

    return results


def print_results_table(results: list[dict[str, Any]]) -> None:
    console = Console()

    table = Table(
        title="TamiTor DSPy ReAct Baseline Results",
        box=box.ROUNDED,
        show_lines=True,
    )

    table.add_column("ID", style="bold", no_wrap=True)
    table.add_column("Category", no_wrap=True)
    table.add_column("Request", overflow="fold")
    table.add_column("Expected", no_wrap=True)
    table.add_column("Called Tools", overflow="fold")
    table.add_column("Response", overflow="fold")
    table.add_column("Tool", justify="center")
    table.add_column("Forbidden", justify="center")
    table.add_column("Clarify", justify="center")

    for result in results:
        called_tools = result.get("called_tools", [])

        called_tools_text = "\n".join(
            call.get("tool_name", str(call))
            for call in called_tools
        ) or "-"

        expected_tool = result.get("expected_tool")
        expected_behavior = result.get("expected_behavior")

        expected_text = (
            f"{expected_behavior}"
            + (f"\n{expected_tool}" if expected_tool else "")
        )

        table.add_row(
            result.get("id", ""),
            result.get("category", ""),
            result.get("request", ""),
            expected_text,
            called_tools_text,
            result.get("response", ""),
            score_cell(result.get("tool_selection_score")),
            violation_cell(result.get("forbidden_tool_violation")),
            score_cell(result.get("clarification_score")),
        )

    console.print(table)


def score_cell(score: float | int | None) -> str:
    if score is None:
        return "-"

    return "✅" if float(score) == 1.0 else "❌"


def violation_cell(value: float | int | None) -> str:
    if value is None:
        return "-"

    return "❌" if float(value) == 1.0 else "✅"

def load_test_examples(path: str) -> list[DatasetExample]:
    import json
    with open(path, "r") as f:
        return [DatasetExample(**json.loads(line)) for line in f]

if __name__ == "__main__":
    path = "data/splits/test.jsonl"
    test_examples = load_test_examples(path)
    
    results = run_baseline(agent, test_examples)
    print(results)
    # results = run_baseline(agent, SEED_EXAMPLES)
    print_results_table(results)