# TamiTor Evaluation Report

## Run Information

| Field    | Value             |
| -------- | ----------------- |
| Model    | openai/gpt-5-mini |
| Dataset  | dev.jsonl         |
| Rows     | 15                |
| Run Date | 2026-06-07        |

---

## Summary

| Metric                  | Value |
| ----------------------- | ----: |
| Rows                    |    15 |
| Avg Score               | 0.967 |
| Behavior Accuracy       | 1.000 |
| Tool Accuracy           | 1.000 |
| Args Accuracy           | 0.933 |
| Missing Fields Accuracy | 0.867 |
| Forbidden Tool Rate     | 0.000 |
| Forbidden Arg Rate      | 0.000 |
| Avg Duration (ms)       |   4.0 |
| Median Duration (ms)    |   1.3 |
| P95 Duration (ms)       |   2.6 |
| Max Duration (ms)       |  40.7 |

---

## Failure Analysis

### book_appointment__complete__v04

**Score:** 0.833

**Failure Type:** args

Expected:

```json
{
  "service": "haircut",
  "date": "Friday",
  "time": "3:30pm",
  "customer_name": "Sarah"
}
```

Actual:

```json
{
  "service": "haircut",
  "date": "2026-06-12",
  "time": "15:30",
  "customer_name": "Sarah"
}
```

Observation:

The model normalized the date and time.

This is likely a dataset issue rather than an agent failure.

---

### book_appointment__missing__service__time__v04

**Score:** 0.833

**Failure Type:** missing_fields

Expected:

```json
["service", "time"]
```

Actual:

```json
["service", "time", "date"]
```

Observation:

The model interpreted "Friday" as insufficient date information.

Need to decide whether weekday references count as complete dates.

---

### reschedule_appointment__missing__time__v04

**Score:** 0.833

**Failure Type:** missing_fields

Expected:

```json
["time"]
```

Actual:

```json
["date", "time"]
```

Observation:

The model did not consider "Friday" sufficient date information.

Same ambiguity appears in multiple rows.

---

## Key Findings

1. Behavior routing is perfect on this dataset (15/15).
2. Tool selection is perfect on this dataset (15/15).
3. Remaining errors are concentrated in:

   * argument normalization
   * missing-field interpretation
4. No hallucinated tool calls were observed.
5. No hallucinated arguments were observed.
6. The dominant source of error appears to be dataset ambiguity rather than tool selection.

---

## Next Actions

1. Normalize date/time expectations in the dataset.
2. Define explicit policy for weekday-only dates.
3. Expand multi-turn scenarios.
4. Add get_active_bookings workflow.
5. Run evaluation on the full dataset.
