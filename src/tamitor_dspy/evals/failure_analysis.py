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

def print_failures(eval_results) -> None:
    failures = [r for r in eval_results if r.score < 1.0]

    table = Table(title=f"Failures ({len(failures)})")

    table.add_column("ID", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Failure Type")
    table.add_column("Notes")

    for r in failures:
        failure_types = []

        if not r.behavior_match:
            failure_types.append("behavior")

        if not r.tool_match:
            failure_types.append("tool")

        if not r.args_match:
            failure_types.append("args")

        if not r.missing_fields_match:
            failure_types.append("missing_fields")

        if r.forbidden_tool_used:
            failure_types.append("forbidden_tool")

        if r.forbidden_arg_used:
            failure_types.append("forbidden_arg")

        duration = f"{r.trace.duration_ms:.1f}ms" if r.trace else "-"

        table.add_row(
            r.id,
            f"{r.score:.3f}",
            duration,
            ", ".join(failure_types),
            "\n".join(r.notes) if r.notes else "-",
        )

    console.print(table)