# Tami Tor DSPy

Evaluation-driven DSPy project for building a WhatsApp appointment assistant for a beauty / treatment business.

The goal of this repo is not to “write the perfect prompt”.

The goal is to define the assistant’s behavior through:

1. dataset
2. metrics
3. baseline evaluation
4. failure analysis
5. optimization
6. regression testing

DSPy ReAct is used as the first baseline agent.

---

## Product Context

Tami Tor receives free-form WhatsApp messages from customers.

Examples:

```text
היי רוצה לקבוע גבות למחר
יש פנוי היום בערב?
אפשר להזיז את התור שלי?
תבטלי לי את התור של יום חמישי
כמה עולה טיפול פנים?
אני לא מצליחה לבחור שעה
אפשר לדבר עם מישהי?
```

The hard part is that these messages often contain partial information.

A good assistant should not rush into tool calls.
It should understand the customer’s intent, detect missing fields, ask precise clarification questions, and avoid inventing availability.

---

## Input Space

The input is a free-form WhatsApp customer message.

In v0, each example is a single user message.

Later versions may include:

* conversation history
* customer profile
* existing appointments
* availability results
* business FAQ knowledge
* human escalation state

---

## Output Space

In v0, the assistant should produce one of six behavior types:

```text
book_appointment
reschedule_appointment
cancel_appointment
answer_faq
handoff_to_human
clarify
```

The important distinction is:

* Tool actions are allowed only when enough information exists.
* Clarification is required when information is missing.
* Handoff is required when the user asks for a human, is angry, confused, or the request is unsupported.

---

## ReAct Tools v0

```python
book_appointment(service, date, time, customer_name)

reschedule_appointment(appointment_id, date, time)

cancel_appointment(appointment_id)

answer_faq(topic)

handoff_to_human(reason)
```

These tools are intentionally minimal.

They do not yet check real availability.
They do not yet retrieve real appointment records.
They are used to measure whether the agent chooses the right behavior.

---

## Expected Behavior

### Booking

If the customer wants to book an appointment and provides:

* service
* date
* time
* customer name

then the assistant may call:

```text
book_appointment(service, date, time, customer_name)
```

If service is missing, ask which service.

If date is missing, ask which day.

If time is missing, ask what time works or say that availability needs to be checked.

If customer name is missing, ask for the customer name.

The assistant must not invent availability.

The assistant must not confirm an appointment unless the booking tool was called.

---

### Reschedule

If the customer wants to move an appointment and provides an appointment identifier plus a new date/time, call:

```text
reschedule_appointment(appointment_id, date, time)
```

If the existing appointment is not identified, ask a question that helps identify it.

Examples:

```text
לאיזה תור את מתכוונת?
אפשר לקבל שם או שעה של התור הקיים?
```

If the new time is missing, ask for the new preferred time.

---

### Cancellation

If the customer wants to cancel and provides an appointment identifier, call:

```text
cancel_appointment(appointment_id)
```

If the appointment is vague, ask which appointment to cancel.

The assistant must not cancel an appointment without identifying which appointment.

---

### FAQ

If the customer asks a simple business question, such as:

* price
* duration
* location
* preparation
* cancellation policy

then call:

```text
answer_faq(topic)
```

The assistant should not convert FAQ questions into booking flows.

Example:

```text
כמה עולה טיפול פנים?
```

Expected behavior:

```text
answer_faq(topic="price: facial treatment")
```

not:

```text
clarify: איזה יום תרצי לקבוע?
```

---

### Human Handoff

If the user asks for a human, is angry, confused, or the request is unsupported, call:

```text
handoff_to_human(reason)
```

Examples:

```text
אפשר לדבר עם מישהי?
אני לא מצליחה לבחור שעה
די נמאס לי, אף אחת לא עונה
```

The assistant should not collapse into human handoff for every slightly ambiguous case.

---

## Important Failure Modes

### 1. Tool Eagerness

The agent calls a tool even though required information is missing.

Example failure:

```text
User: רוצה לקבוע גבות
Bad: book_appointment(service="גבות")
Good: clarify missing date/time/name
```

---

### 2. Clarification Overuse

The agent asks a question even though the information already exists.

Example failure:

```text
User: אני דנה, רוצה גבות מחר בשש
Bad: איך קוראים לך?
Good: book_appointment(...)
```

---

### 3. Wrong Intent

The agent confuses similar intents.

Example failure:

```text
User: אפשר להזיז את התור שלי?
Bad: book_appointment
Good: clarify/reschedule
```

---

### 4. Missing Identity

The agent modifies or cancels an appointment without identifying the existing appointment.

Example failure:

```text
User: תבטלי לי את התור
Bad: cancel_appointment(...)
Good: clarify which appointment
```

---

### 5. Availability Hallucination

The agent proposes or confirms times that did not come from an availability tool.

Example failure:

```text
User: יש פנוי היום בערב?
Bad: כן, יש ב-19:00
Good: clarify/check availability needed
```

In v0 there is no availability tool, so the agent must not invent available times.

---

### 6. Premature Confirmation

The agent says an appointment was booked, changed, or cancelled without calling the correct tool.

---

### 7. FAQ Leakage

A price, duration, location, or policy question accidentally becomes a booking flow.

---

### 8. Human Fallback Collapse

The agent sends too many cases to a human instead of handling simple clarification or FAQ behavior.

---

## Dataset First

The dataset defines the behavior space.

It is not just a list of examples.

Each example should specify:

* input message
* expected behavior type
* expected tool, if any
* expected required args
* missing fields
* forbidden tools
* forbidden args
* notes explaining the behavioral boundary

---

## Dataset Categories v0

### 1. complete_booking

Cases where booking has all required fields.

Required fields:

* service
* date
* time
* customer identity

Expected behavior:

```text
book_appointment
```

---

### 2. incomplete_booking

Booking intent exists, but one or more fields are missing.

Subcategories:

```text
missing_service
missing_date
missing_time
missing_customer_name
missing_multiple_fields
```

Expected behavior:

```text
clarify
```

---

### 3. reschedule

Customer wants to move an existing appointment.

Subcategories:

```text
has_appointment_id_and_new_time
has_customer_name_and_vague_appointment
missing_new_time
missing_existing_appointment
```

Expected behavior:

```text
reschedule_appointment
```

or:

```text
clarify
```

depending on whether enough information exists.

---

### 4. cancel

Customer wants to cancel an appointment.

Subcategories:

```text
explicit_appointment_id
vague_appointment
same_day_cancellation
angry_cancellation
```

Expected behavior:

```text
cancel_appointment
```

or:

```text
clarify
```

or:

```text
handoff_to_human
```

depending on context.

---

### 5. faq

Customer asks a business information question.

Subcategories:

```text
price
duration
location
preparation
cancellation_policy
```

Expected behavior:

```text
answer_faq
```

---

### 6. handoff_or_confusion

Customer asks for a person, expresses frustration, confusion, or asks for something unsupported.

Subcategories:

```text
asks_for_human
complaint
confusion
unsupported_request
```

Expected behavior:

```text
handoff_to_human
```

---

## Metrics v0

Do not start with generic accuracy.

Generic accuracy hides the most important problems.

Use targeted metrics.

---

### 1. intent_accuracy

Measures whether the assistant selected the correct high-level behavior.

Examples:

```text
book_appointment
reschedule_appointment
cancel_appointment
answer_faq
handoff_to_human
clarify
```

---

### 2. tool_selection_accuracy

Measures whether the assistant called the correct tool when a tool call is expected.

Also checks that no tool was called when clarification was expected.

---

### 3. required_args_accuracy

Measures whether required tool arguments were correctly extracted.

Example:

```json
{
  "service": "גבות",
  "date": "מחר",
  "time": "18:00",
  "customer_name": "דנה"
}
```

---

### 4. clarification_correctness

Measures whether the clarification question targets the actually missing field.

Example:

```text
User: רוצה לקבוע גבות מחר
Expected: ask for time and/or name
Bad: ask which service
```

---

### 5. forbidden_action_violation_rate

Measures safety and business-rule violations.

Examples:

* booking without missing fields
* cancelling without appointment identity
* inventing availability
* confirming without a tool call
* sending easy FAQ cases to human handoff

This metric should trend toward zero.

---

## First Development Loop

The first loop is intentionally simple.

```text
dataset
→ metrics
→ baseline DSPy ReAct
→ failure analysis
→ improve dataset/metrics/tool descriptions
→ rerun baseline
→ only then optimize
```

---

## Initial Goal

The first milestone is not to get a high score.

The first milestone is to discover where the behavior is not yet measurable.

Questions to answer:

1. Is the dataset clear?
2. Are expected behaviors unambiguous?
3. Are the metrics catching the important failures?
4. Is DSPy ReAct too eager to call tools?
5. Are tool descriptions too weak?
6. Do we need state?
7. Do we need appointment retrieval?
8. Do we need availability retrieval?
9. Do we need a separate classifier before ReAct?
10. Which failures are caused by model behavior vs. dataset ambiguity?

---

## Repo Philosophy

This repo follows evaluation-driven development.

Prompts are not the source of truth.

The dataset and metrics are the source of truth.

DSPy optimization should only begin after there is a measurable baseline.

---

## Suggested v0 Success Criteria

Before optimization:

```text
baseline runs end-to-end
all examples are evaluated
failure report is generated
metrics are separated by category
forbidden action violations are visible
```

After optimization:

```text
improved dev score
no regression on critical violations
held-out test set remains clean
clarification behavior improves
tool eagerness decreases
```

---

## Non-Goals for v0

v0 does not need:

* real WhatsApp integration
* real calendar integration
* real availability search
* production database
* multi-user support
* authentication
* complex LangGraph orchestration
* advanced memory
* RAG

Those may come later, after the behavior is measurable.

---

## Future Directions

Possible v1 additions:

* availability tool
* appointment lookup tool
* conversation state
* customer identity memory
* FAQ retrieval
* train/dev/test split
* DSPy optimizer
* regression suite
* Hebrew normalization
* ambiguity tagging
* multi-turn dataset
* human handoff policy evaluator
