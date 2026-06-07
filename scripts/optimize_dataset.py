# scripts/evaluate_dataset.py

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
import dspy

from src.tamitor_dspy.agents.signatures import TamiTorPredict, TamiTorTurnDecision
from src.tamitor_dspy.models.labeled import DatasetRow
from src.tamitor_dspy.evals.metrics import evaluate_prediction, weighted_metric
from src.tamitor_dspy.models.prediction import PredictionTrace
from src.tamitor_dspy.evals.failure_analysis import print_failures
from src.tamitor_dspy.evals.summary import print_summary

def evaluation_result_to_eval_results(
    evaluation_result,
) -> list[Any]:
    results = []

    for example, prediction, _ in evaluation_result.results:
        results.append(
            evaluate_prediction(
                row=example._row,
                prediction=prediction.result,
            )
        )

    return results

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
    lm = dspy.LM("openai/gpt-5.4-mini", cache=True)
    print(lm.model)
    dspy.configure(lm=lm)

    predict = dspy.Predict(TamiTorTurnDecision)

    train_rows = load_jsonl(Path("data/splits/train.jsonl"))
    train_examples = []
    for row in train_rows:
        ex = dspy.Example(turn=row.input).with_inputs("turn")
        ex._row = row
        train_examples.append(ex)

    dev_rows = load_jsonl(Path("data/splits/dev.jsonl"))
    dev_examples = []
    for row in dev_rows:
        ex = dspy.Example(turn=row.input).with_inputs("turn")
        ex._row = row
        dev_examples.append(ex)

    evaluator = dspy.Evaluate(devset=dev_examples, metric=weighted_metric,
                                num_threads=2, display_progress=False)

   

    baseline_score = evaluator(predict)
     # Baseline — note: ChainOfThought hurts here, model talks itself into wrong tier
    print("\n" + "=" * 80)
    print(f"Baseline:  {baseline_score.score:.1f}%")
    print("=" * 80 + "\n")
    eval_results = evaluation_result_to_eval_results(baseline_score)
    print_summary(eval_results)
    print_failures(eval_results)
    
    # LabeledFewShot — k=4 demos, no LM calls during compile
    optimizer = dspy.LabeledFewShot(k=6)
    compiled_lfs  = optimizer.compile(predict, trainset=train_examples)
    print("\n" + "=" * 80)
    print(f"LabeledFewShot:  {evaluator(compiled_lfs).score:.1f}%")
    print(f"LabeledFewShot demos {len(compiled_lfs.demos)}:")
    #print(compiled_lfs.demos)
    print("=" * 80 + "\n")

    optimizer = dspy.BootstrapFewShot(metric=weighted_metric)
    compiled_bfs  = optimizer.compile(predict, trainset=train_examples)

    print("\n" + "=" * 80)
    print(f"BootstrapFewShot:  {evaluator(compiled_bfs).score:.1f}%")
    print("=" * 80 + "\n")
    print(f"BootstrapFewShot demos {len(compiled_bfs.demos)}:")
    #print(compiled_bfs.demos)
    print("=" * 80 + "\n")

    vectorizer = dspy.Embedder("openai/text-embedding-3-small")
    knn_optimizer = dspy.KNNFewShot(k=6, trainset=train_examples, vectorizer=vectorizer)
    knn_compiled  = knn_optimizer.compile(predict)
    knn_score     = evaluator(knn_compiled)
    print(f"KNNFewShot:           {knn_score.score:.1f}%  ")

    eval_results = evaluation_result_to_eval_results(
        knn_score
    )

    print_summary(eval_results)
    print_failures(eval_results)

if __name__ == "__main__":
    main()