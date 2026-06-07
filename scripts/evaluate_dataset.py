# scripts/evaluate_dataset.py

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import dspy

from src.tamitor_dspy.agents.signatures import TamiTorPredict, TamiTorTurnDecision
from src.tamitor_dspy.models.labeled import DatasetRow
from src.tamitor_dspy.evals.metrics import evaluate_prediction
from src.tamitor_dspy.models.prediction import PredictionTrace
from src.tamitor_dspy.evals.failure_analysis import print_failures
from src.tamitor_dspy.evals.summary import print_summary


def load_jsonl(path: Path) -> list[DatasetRow]:
    rows: list[DatasetRow] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                rows.append(DatasetRow.model_validate_json(line))
            except Exception as e:
                raise ValueError(f"Failed parsing {path}:{line_no}: {e}") from e

    return rows


def run_one(row: DatasetRow, predict: dspy.Predict):
    started_at = datetime.now(timezone.utc)
    t0 = perf_counter()
    print(row.input.model_dump_json(indent=2))
    prediction = predict(turn=row.input)

    duration_ms = (perf_counter() - t0) * 1000
    finished_at = datetime.now(timezone.utc)

    eval_result = evaluate_prediction(row, prediction)
    eval_result.trace = PredictionTrace(
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
    )

    return prediction, eval_result


def summarize(eval_results):
    n = len(eval_results)

    if n == 0:
        return {}

    return {
        "num_rows": n,
        "avg_score": sum(r.score for r in eval_results) / n,
        "behavior_accuracy": sum(r.behavior_match for r in eval_results) / n,
        "tool_accuracy": sum(r.tool_match for r in eval_results) / n,
        "args_accuracy": sum(r.args_match for r in eval_results) / n,
        "missing_fields_accuracy": sum(r.missing_fields_match for r in eval_results) / n,
        "forbidden_tool_rate": sum(r.forbidden_tool_used for r in eval_results) / n,
        "forbidden_arg_rate": sum(r.forbidden_arg_used for r in eval_results) / n,
        "avg_duration_ms": sum(r.trace.duration_ms for r in eval_results if r.trace) / n,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Path to dataset jsonl file.",
    )
    parser.add_argument(
        "--model",
        default="openai/gpt-5.4-mini",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("runs/eval_results.jsonl"),
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=Path("runs/eval_summary.json"),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--print-failures",
        action="store_true",
    )

    args = parser.parse_args()

    lm = dspy.LM(args.model, cache=False)
    print(lm.model)
    dspy.configure(lm=lm)

    predict = TamiTorPredict()

    rows = load_jsonl(args.dataset)

    if args.limit is not None:
        rows = rows[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)

    eval_results = []

    with args.out.open("w", encoding="utf-8") as f:
        #cold start
        _, _ = run_one(rows[0], predict)

        for i, row in enumerate(rows, start=1):
            prediction, eval_result = run_one(row, predict)
            eval_results.append(eval_result)

            record = {
                "row_id": row.id,
                "prediction": prediction.model_dump(mode="json")
                if hasattr(prediction, "model_dump")
                else str(prediction),
                "eval": eval_result.model_dump(mode="json"),
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            if args.print_failures and eval_result.score < 1.0:
                print(f"\nFAIL {row.id} score={eval_result.score}")
                print(json.dumps(eval_result.model_dump(mode="json"), indent=2, ensure_ascii=False))

            print(f"[{i}/{len(rows)}] {row.id} score={eval_result.score:.3f}")

    print_summary(eval_results)
    print_failures(eval_results)
   

if __name__ == "__main__":
    main()