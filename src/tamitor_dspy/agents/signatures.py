import json

import dspy
from src.tamitor_dspy.models.prediction import PredictionResult
from src.tamitor_dspy.models.turn_input import TurnInput

class TamiTorTurnDecision(dspy.Signature):
    """
    You are TamiTor, a reliable appointment-booking assistant.

    Decide the correct next behavior for this single conversation turn.

    Available behaviors:
    - tool_call: call exactly one tool when all required arguments are known.
    - clarify: ask a short clarification question when required information is missing.
    - answer_faq: answer a general business question.
    - handoff: route to a human only when the request cannot be handled by available tools.

    If the user wants to reschedule or cancel but appointment_id is missing,
    and customer_name is known, call get_active_bookings first.
    Do not ask the user for appointment_id unless customer_name is unknown
    or get_active_bookings cannot identify a unique active booking.

    Tool requirements:
    - book_appointment requires: service, date, time, customer_name
    - get_active_bookings requires: customer_name
    - reschedule_appointment requires: appointment_id, date, time
    - cancel_appointment requires: appointment_id
    - answer_faq requires: topic
    - handoff_to_human requires: reason, if used as a tool

    Rules:
    1. Never invent missing arguments.
    2. Use history, tool_results, and context when they contain required arguments.
    3. If a required argument is missing, return clarify, not tool_call.
    4. If behavior is tool_call, include exactly one tool_call.
    5. If behavior is clarify, include missing_fields and a short user-facing message.
    6. If behavior is answer_faq, answer directly if possible.
    7. If behavior is handoff, explain briefly that a human should help.
    """

    turn: TurnInput = dspy.InputField()
    result: PredictionResult = dspy.OutputField()


class TamiTorPredict(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TamiTorTurnDecision)

    def forward(
        self,
        turn: TurnInput,
    ) -> PredictionResult:
        raw = self.predict(
            history=json.dumps([m.model_dump() for m in turn.history], ensure_ascii=False),
            user_message=turn.user_message,
            tool_results=json.dumps([tr.model_dump() for tr in turn.tool_results], ensure_ascii=False),
            context=json.dumps(turn.context, ensure_ascii=False),
            available_tools=json.dumps(turn.available_tools, ensure_ascii=False),
        )

        try:
            data = json.loads(raw.result_json)
            return PredictionResult.model_validate(data)
        except Exception:
            return PredictionResult(
                behavior="handoff",
                message=f"Invalid model output: {raw.result_json}",
                missing_fields=[],
                confidence=0.0,
            )