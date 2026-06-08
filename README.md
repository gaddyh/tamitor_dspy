# TamiTor DSPy

Evaluation-Driven Development (EDD) of a Tool-Calling Appointment Scheduling Agent.

---

# Why This Project Exists

Most agent projects start with prompts.

This project starts with a different question:

> How do we know whether an agent is improving?

Instead of manually tweaking prompts and hoping for better behavior, TamiTor treats agent development as an evaluation problem.

The goal is to build a measurable appointment-booking assistant and improve it through datasets, metrics, failure analysis, and optimization.

---

# Problem

TamiTor is an appointment scheduling assistant for small businesses.

The assistant can:

* Book appointments
* Reschedule appointments
* Cancel appointments
* Answer FAQ questions
* Escalate to a human when needed

Example requests:

* "Book a haircut for Sarah on Friday at 3:30pm"
* "Move my appointment to next week"
* "Cancel my appointment"
* "What services do you offer?"

---

# Philosophy

The development process follows:

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

The objective is not to find a better prompt.

The objective is to build a system whose behavior can be measured and improved.

---

# Current Architecture

The current version evaluates a single conversation turn.

Input:

```python
TurnInput
```

Contains:

* user message
* conversation history
* tool results
* runtime context
* available tools

Output:

```python
PredictionResult
```

Contains:

* behavior
* tool call
* arguments
* missing fields
* confidence

---

# Behaviors

The agent can return one of four behaviors:

```text
tool_call
clarify
answer_faq
handoff
```

Example:

```text
User:
Book a haircut tomorrow.

Agent:
clarify

Missing:
time
customer_name
```

---

# Dataset Design

Each dataset row defines expected behavior for a single decision point.

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

The dataset intentionally separates:

* intent detection
* argument extraction
* missing-field detection
* action readiness

---

# Why Turn-Level Evaluation?

Many agent benchmarks evaluate only the final outcome of a conversation.

This project evaluates individual decision points.

The goal is to understand why an agent failed rather than simply whether it failed.

A turn-level benchmark makes it possible to measure:

* Intent understanding
* Argument extraction
* Missing-field detection
* Readiness decisions
* Safety violations

This allows failures to be localized and optimized independently.

The benchmark therefore focuses on behavioral correctness at each step rather than only end-to-end task success.

---

# Metrics

The project evaluates more than simple accuracy.

## Core Metrics

* Behavior Accuracy
* Tool Accuracy
* Argument Accuracy
* Missing Field Accuracy

## Safety Metrics

* Forbidden Tool Rate
* Forbidden Argument Rate

## Readiness Metrics

* Readiness Accuracy
* Premature Action Rate
* Unnecessary Clarification Rate

---

# Weighted Scoring

Not all mistakes are equally harmful.

### Mild Failure

Expected:

```text
missing:
service,time
```

Predicted:

```text
missing:
service
```

Annoying but recoverable.

### Severe Failure

Expected:

```text
clarify
```

Predicted:

```text
reschedule_appointment(...)
```

Potentially modifies a real booking.

Weighted scoring penalizes unsafe actions significantly more than extraction mistakes.

---

# First Real Failure Mode

The benchmark revealed a recurring failure pattern:

```text
The model acted before it was ready.
```

Examples included:

* Rescheduling without a time
* Rescheduling without a date
* Answering a FAQ without a topic

We refer to this behavioral tension as:

```text
Act
vs
Clarify
```

---

# From Failure to Metric

An experienced engineer might predict that a scheduling agent will struggle with deciding when to act and when to ask for more information.

However, the goal of this project is not to rely on intuition.

The goal is to verify behavioral hypotheses through evaluation.

The initial assumption was that tool selection or argument extraction would be the primary sources of error.

The first benchmark revealed something different.

The model generally:

* Selected the correct tool
* Extracted arguments correctly
* Understood the user's intent

Yet it still failed.

Failure analysis showed that many errors shared a common pattern:

```text
The model acted before it was ready.
```

This led to a new hypothesis:

```text
The dominant challenge is not tool selection.

The dominant challenge is readiness.
```

More specifically:

```text
Act
vs
Clarify
```

At this point the project shifted from measuring correctness to measuring readiness.

New metrics were introduced:

* Readiness Accuracy
* Premature Action Rate
* Forbidden Tool Rate
* Forbidden Argument Rate

A weighted score was then created to reflect business risk.

The weighted score intentionally penalizes unsafe actions more heavily than extraction mistakes.

In effect, the metric encodes the following preference:

> Asking one additional clarification question is preferable to executing one unsafe action.

This was the first example of a behavioral hypothesis being transformed into a measurable optimization target.

Rather than optimizing prompts directly, the project first identified a failure mode, translated it into metrics, and then optimized against those metrics.

---

# Optimization Results

## Understanding the Tension

When information is incomplete, the agent faces two competing objectives.

### Objective 1: Be Helpful

Move the conversation forward.

Avoid unnecessary questions.

Complete the task quickly.

This objective pushes the model toward:

```text
ACT
```

### Objective 2: Be Safe

Avoid assumptions.

Avoid hallucinated arguments.

Avoid modifying bookings with incomplete information.

This objective pushes the model toward:

```text
CLARIFY
```

These objectives are inherently in conflict.

A model that always acts will occasionally perform unsafe actions.

A model that always clarifies will become frustrating and inefficient.

The challenge is finding the correct balance.

---

## Designing Better Metrics

The original metric treated all mistakes equally.

Failure analysis showed that different mistakes carry very different business risks.

A clarification mistake is usually recoverable.

A premature action may modify or cancel a real appointment.

To better reflect product risk, the evaluation framework was extended with:

* Readiness Accuracy
* Premature Action Rate
* Forbidden Tool Rate
* Forbidden Argument Rate

A weighted scoring system was introduced.

---

## Optimization Experiments

| Strategy         | Score |
| ---------------- | ----: |
| Baseline         | 77.9% |
| LabeledFewShot   | 77.9% |
| BootstrapFewShot | 82.1% |
| KNNFewShot       | 90.0% |

Notably, simple few-shot examples produced no measurable improvement.

The largest gains came from selecting behaviorally similar demonstrations through KNNFewShot.

---

## What the Optimizer Taught Us

An unexpected finding emerged during the optimization experiments.

KNNFewShot consistently produced the strongest results.

This is interesting because KNNFewShot performs almost no instruction engineering.

Its primary contribution is selecting behaviorally similar examples.

This suggests that the primary bottleneck in the current system is not instruction quality.

Instead, the missing information appears to be contained in the examples themselves.

In other words:

* The model already understands scheduling.
* The model already understands tools.
* The model already understands English.

What it does not fully understand is how TamiTor defines readiness.

The optimizer therefore improved performance primarily by exposing the model to better demonstrations of the desired behavior rather than by generating better instructions.

This observation reinforced an important EDD principle:

> When failures are caused by unclear behavior boundaries, improving the dataset is often more valuable than improving the prompt.

---

## What Improved

| Metric                | Baseline | KNNFewShot |
| --------------------- | -------: | ---------: |
| Avg Weighted Score    |    0.779 |      0.900 |
| Readiness Accuracy    |    0.800 |      0.867 |
| Premature Action Rate |    0.200 |      0.133 |
| Args Accuracy         |    1.000 |      1.000 |

Optimization primarily improved readiness decisions rather than extraction quality.

---

## Key Insight

```text
Tool Selection
≠
Tool Readiness
```

A model may know exactly which tool to use and still fail because it executes the tool before gathering sufficient information.

The dominant behavioral challenge identified in this benchmark is therefore:

```text
Act
vs
Clarify
```

---

# What We Learned

The strongest signal so far is not tool selection.

The strongest signal is:

```text
Act
vs
Clarify
```

The optimization process improved behavior primarily by reducing premature actions rather than improving argument extraction.

This suggests that readiness gating is a major source of error for tool-calling agents.

---

# Current Status

## Completed

* Dataset schema
* Turn-level evaluator
* Rich failure reporting
* Weighted scoring
* Readiness metrics
* DSPy optimization experiments
* KNNFewShot benchmark

## In Progress

* Expand dataset coverage
* Build train/dev/test split
* Increase scenario diversity
* Add multi-turn examples

## Planned

* MIPROv2 optimization
* Larger benchmark datasets
* Architecture comparisons
* End-to-end conversation evaluation

---

# Key Takeaway

This project is not about building another chatbot.

It is an exploration of how to evaluate, understand, and improve agent behavior through datasets, metrics, failure analysis, and measurable optimization.

The central lesson so far is simple:

```text
Find the failure.
Turn it into a metric.
Optimize against the metric.
Measure again.
```
