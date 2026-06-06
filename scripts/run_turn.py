import dspy

from src.tamitor_dspy.agents.signatures import TamiTorTurnDecision
from src.tamitor_dspy.evals.metrics import evaluate_prediction
from src.tamitor_dspy.models.prediction import PredictionTrace
from data.schemas.seed_examples import full_details_example, missing_time_example
from datetime import datetime, timezone
from time import perf_counter



lm = dspy.LM("openai/gpt-5-mini")
dspy.configure(lm=lm)

predict = dspy.Predict(TamiTorTurnDecision)

row = full_details_example

started_at = datetime.now(timezone.utc)
t0 = perf_counter()
result = predict(turn=row.input)
duration_ms = (perf_counter() - t0) * 1000
finished_at = datetime.now(timezone.utc)

print(result)

eval_result = evaluate_prediction(row, result)

eval_result.trace = PredictionTrace(
    started_at=started_at,
    finished_at=finished_at,
    duration_ms=duration_ms,
)
print(eval_result.model_dump_json(indent=2))


row = missing_time_example
started_at = datetime.now(timezone.utc)
t0 = perf_counter()
result = predict(turn=row.input)
duration_ms = (perf_counter() - t0) * 1000
finished_at = datetime.now(timezone.utc)
print(result)
eval_result = evaluate_prediction(row, result)
eval_result.trace = PredictionTrace(
    started_at=started_at,
    finished_at=finished_at,
    duration_ms=duration_ms,
)
print(eval_result.model_dump_json(indent=2))


row = full_details_example

started_at = datetime.now(timezone.utc)
t0 = perf_counter()
result = predict(turn=row.input)
duration_ms = (perf_counter() - t0) * 1000
finished_at = datetime.now(timezone.utc)

print(result)

eval_result = evaluate_prediction(row, result)

eval_result.trace = PredictionTrace(
    started_at=started_at,
    finished_at=finished_at,
    duration_ms=duration_ms,
)
print(eval_result.model_dump_json(indent=2))

