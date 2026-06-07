from statistics import mean, median
from rich.console import Console
from rich.table import Table

console = Console()


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return values[0]

    index = round((p / 100) * (len(values) - 1))
    return values[index]


def rate(eval_results, attr: str) -> float:
    if not eval_results:
        return 0.0

    return sum(bool(getattr(r, attr)) for r in eval_results) / len(eval_results)


def print_summary(eval_results) -> None:
    if not eval_results:
        console.print("[yellow]No eval results.[/yellow]")
        return

    durations = [
        r.trace.duration_ms
        for r in eval_results
        if r.trace is not None
    ]

    table = Table(title="Dataset Evaluation Summary")

    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Rows", str(len(eval_results)))

    table.add_row("Avg Simple Score", f"{mean(r.score for r in eval_results):.3f}")
    table.add_row("Avg Weighted Score", f"{mean(r.weighted_score for r in eval_results):.3f}")
    table.add_row("Readiness Accuracy", f"{rate(eval_results, 'readiness_match'):.3f}")
    table.add_row("Premature Action Rate", f"{rate(eval_results, 'premature_action'):.3f}")
    table.add_row("Unnecessary Clarification Rate", f"{rate(eval_results, 'unnecessary_clarification'):.3f}")

    table.add_row("Behavior Accuracy", f"{rate(eval_results, 'behavior_match'):.3f}")
    table.add_row("Tool Accuracy", f"{rate(eval_results, 'tool_match'):.3f}")
    table.add_row("Args Accuracy", f"{rate(eval_results, 'args_match'):.3f}")
    table.add_row("Missing Fields Accuracy", f"{rate(eval_results, 'missing_fields_match'):.3f}")

    table.add_row("Forbidden Tool Rate", f"{rate(eval_results, 'forbidden_tool_used'):.3f}")
    table.add_row("Forbidden Arg Rate", f"{rate(eval_results, 'forbidden_arg_used'):.3f}")

    if durations:
        table.add_row("Avg Duration (ms)", f"{mean(durations):.1f}")
        table.add_row("Median Duration (ms)", f"{median(durations):.1f}")
        table.add_row("P95 Duration (ms)", f"{percentile(durations, 95):.1f}")
        table.add_row("Max Duration (ms)", f"{max(durations):.1f}")

    console.print(table)


