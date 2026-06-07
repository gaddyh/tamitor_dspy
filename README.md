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

Example:

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

The first benchmark revealed an important behavioral tension:

```text
Act
vs
Clarify
```

Some models prefer to act before collecting all required information.

Examples:

* Reschedule without time
* Reschedule without date
* FAQ without a clear topic

This became the first measurable failure mode in the project.

---

# Baseline Results

Model:

```text
openai/gpt-5.4-mini
```

Development Set:

```text
Rows: 15
```

Results:

| Metric                | Score |
| --------------------- | ----: |
| Avg Weighted Score    | 0.779 |
| Readiness Accuracy    | 0.800 |
| Premature Action Rate | 0.200 |
| Args Accuracy         | 1.000 |

Key finding:

The model extracted arguments correctly but often acted before all required information was available.

---

# Optimization Results

The optimization phase did not begin by changing prompts or searching for better instructions.

Instead, it began with failure analysis.

## Discovering a Behavioral Tension

Initial evaluation revealed that the dominant failure mode was not intent classification and not argument extraction.

In most failing examples, the model correctly understood:

* Which tool should eventually be used
* Which arguments were already known
* What the user was trying to accomplish

However, the model often executed the tool before collecting all required information.

For example:

Expected:

```text
Behavior: clarify
Missing: time
```

Predicted:

```text
Behavior: tool_call
Tool: reschedule_appointment
```

The model knew the correct tool, but acted before it was ready.

This revealed a deeper behavioral tension:

```text
Act
vs
Clarify
```

or more generally:

```text
Execution
vs
Information Gathering
```

---

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

For example:

```text
Missing field mismatch
```

and

```text
Premature tool execution
```

received similar penalties.

Failure analysis showed that these errors have very different business consequences.

A clarification mistake is usually recoverable.

A premature action may modify or cancel a real appointment.

To better reflect product risk, the evaluation framework was extended with:

* Readiness Accuracy
* Premature Action Rate
* Forbidden Tool Rate
* Forbidden Argument Rate

A weighted scoring system was introduced.

---

## Weighted Scoring

The weighted metric intentionally penalizes unsafe actions more heavily than extraction mistakes.

The goal was not to maximize tool usage.

The goal was to encourage safe readiness decisions.

Conceptually:

```text
Unsafe Action
    ↓
Large Penalty

Clarification
    ↓
Small Penalty
```

The weighted score therefore became a formal representation of the behavioral tension identified during failure analysis.

In practice, the metric communicates the following preference to the optimizer:

> Asking one additional clarification question is preferable to executing an unsafe action.

---

## Optimization Experiments

Several DSPy optimization strategies were evaluated.

| Strategy         | Score |
| ---------------- | ----: |
| Baseline         | 77.9% |
| LabeledFewShot   | 77.9% |
| BootstrapFewShot | 82.1% |
| KNNFewShot       | 90.0% |

Notably, simple few-shot examples produced no measurable improvement.

The largest gains came from selecting behaviorally similar demonstrations through KNNFewShot.

---

## What Improved

The primary improvements were not in argument extraction.

Argument extraction was already near perfect.

Instead, optimization improved the model's ability to determine whether enough information had been gathered before acting.

| Metric                | Baseline | KNNFewShot |
| --------------------- | -------: | ---------: |
| Avg Weighted Score    |    0.779 |      0.900 |
| Readiness Accuracy    |    0.800 |      0.867 |
| Premature Action Rate |    0.200 |      0.133 |
| Args Accuracy         |    1.000 |      1.000 |

This indicates that the optimization primarily improved readiness decisions rather than extraction quality.

---

## Key Insight

The most important discovery of the project so far is that:

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

The evaluation framework, weighted metric, and optimization process were all developed to measure and improve this specific cognitive tension.


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

Completed:

* Dataset schema
* Turn-level evaluator
* Rich failure reporting
* Weighted scoring
* Readiness metrics
* DSPy optimization experiments
* KNNFewShot benchmark

In Progress:

* Expand dataset coverage
* Build train/dev/test split
* Increase scenario diversity
* Add multi-turn examples

Planned:

* MIPROv2 optimization
* Larger benchmark datasets
* Architecture comparisons
* End-to-end conversation evaluation

---

# Key Takeaway

This project is not about building another chatbot.

It is an exploration of how to evaluate, understand, and improve agent behavior using measurable feedback rather than manual prompt engineering.
