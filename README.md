# TamiTor DSPy

Evaluation-driven development of a tool-calling appointment scheduling agent.

## Motivation

Most agent demos focus on successful conversations.

This project focuses on something different:

* How do we measure agent behavior?
* How do we identify failure modes?
* How do we improve an agent without guessing prompt changes?
* How do we know an optimization actually helped?

The goal is to apply evaluation-driven development (EDD) principles to a realistic appointment scheduling assistant.

Inspired by benchmarks such as TAU2, the project treats agent behavior as a measurable dataset rather than a collection of prompts.

---

## Problem

TamiTor is an appointment scheduling assistant for small businesses.

The assistant can:

* book appointments
* reschedule appointments
* cancel appointments
* answer FAQ questions
* hand off to a human

Example user requests:

* "Book a haircut for Sarah on Friday at 3:30pm"
* "Move my appointment to next week"
* "Cancel my appointment"
* "What services do you offer?"

---

## Approach

Instead of evaluating only final conversations, TamiTor evaluates behavior at the turn level.

Each dataset row represents a single decision point.

Input:

* conversation history
* latest user message
* tool results
* runtime context
* available tools

Expected output:

* behavior
* tool selection
* tool arguments
* missing fields

This makes failures measurable and debuggable.

---

## Dataset

Each example is represented as:

```python
DatasetRow(
    id=...,
    input=TurnInput(...),

    expected_behavior=...,
    expected_tool=...,
    expected_args=...,

    expected_missing_fields=...,

    forbidden_tools=...,
    forbidden_args=...,
)
```

The dataset currently covers:

### Booking

* complete booking
* missing service
* missing date
* missing time
* missing customer

### Rescheduling

* complete reschedule
* missing appointment id
* missing date
* missing time

### Cancellation

* complete cancellation
* missing appointment id

### FAQ

* answerable questions
* missing topic

### Handoff

* explicit request for a human
* transfer requests

---

## Agent

Current baseline:

```text
DSPy Predict
```

The agent receives:

```python
TurnInput
```

and returns:

```python
PredictionResult
```

containing:

* behavior
* tool call
* missing fields
* response message
* confidence

---

## Evaluation

Each prediction is evaluated against ground truth.

Metrics:

### Behavior Accuracy

Did the agent choose:

* tool_call
* clarify
* answer_faq
* handoff

correctly?

### Tool Accuracy

Did the agent select the correct tool?

### Argument Accuracy

Did the agent extract the correct arguments?

### Missing Field Accuracy

Did the agent correctly identify missing information?

### Forbidden Tool Rate

Did the agent call a tool that should not be called?

### Forbidden Argument Rate

Did the agent hallucinate arguments?

---

## Runtime Metrics

Each prediction is timed.

Reported statistics:

* Average Duration
* Median Duration
* P95 Duration
* Max Duration

This allows tracking the tradeoff between:

```text
Accuracy
vs
Latency
```

during optimization.

---

## Example Results

Current development dataset:

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

Most remaining failures are dataset-specification ambiguities rather than routing failures.

Examples:

* Friday vs 2026-06-12
* 3:30pm vs 15:30
* weekday-only date interpretation

---

## Project Structure

```text
src/
├── agents/
│   └── signatures.py
│
├── datasets/
│   ├── schemas.py
│   └── seed_examples.py
│
├── evals/
│   └── metrics.py
│
├── models/
│   └── prediction.py
│
└── scripts/
    ├── run_turn.py
    └── evaluate_dataset.py
```

---

## Current Status

Completed:

* Dataset schema
* Turn-level evaluation framework
* DSPy baseline agent
* Runtime measurement
* Failure reporting
* Markdown reporting

Planned:

* Multi-turn dataset
* Appointment lookup tool
* DSPy optimization
* Train/dev/test split
* Failure clustering
* Architecture comparisons
* TAU2-style workflow evaluation

---

## Philosophy

The project follows evaluation-driven development:

```text
Dataset
    ↓
Baseline
    ↓
Metrics
    ↓
Failure Analysis
    ↓
Optimization
    ↓
Re-Evaluation
```

The objective is not to write better prompts.

The objective is to build measurable and improvable agent behavior.
