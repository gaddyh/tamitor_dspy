import dspy
import uuid
from pydantic import BaseModel
from typing import Any
from src.tamitor_dspy.agents.schemas import DatasetExample
from src.tamitor_dspy.tools.registry import extract_tool_calls_from_trajectory
from src.tamitor_dspy.datasets.seed_examples import SEED_EXAMPLES

lm = dspy.LM("openai/gpt-5.4-mini")

dspy.configure(lm=lm)

def book_appointment(service:str, date:str, time:str, customer_name:str):
    guid = uuid.uuid4()
    res = f"Appointment booked with id {guid} for {customer_name or '--missing name--'} for {service or '--missing service--'} on {date or '--missing date--'} at {time or '--missing time--'}"
    print(res)
    return res

def reschedule_appointment(appointment_id:str, date:str, time:str):
    res = f"Appointment {appointment_id} rescheduled to {date} at {time}"
    print(res)
    return res

def cancel_appointment(appointment_id:str):
    res = f"Appointment {appointment_id} cancelled"
    print(res)
    return res

def answer_faq(topic:str):
    res = f"FAQ answer for {topic}"
    print(res)
    return res

class AgentRun(BaseModel):
    response: str
    called_tools: list[dict[str, Any]]
    raw_trajectory: dict[str, Any]

def run_agent_on_example(agent, example: DatasetExample) -> AgentRun:
    result = agent(
        request=example.request,
        context=example.context,
    )

    called_tools = extract_tool_calls_from_trajectory(result.trajectory)

    return AgentRun(
        response=result.response,
        called_tools=called_tools,
        raw_trajectory=result.trajectory,
    )

class TamiTorReAct(dspy.Signature):
    request: str = dspy.InputField(desc="The user request to classify")
    context: str = dspy.InputField(desc="The context of the user request")
    response: str = dspy.OutputField(desc="The response to the user request")

TamiTorReAct = TamiTorReAct.with_instructions(
    f"""You are a helpful booking assistant. You help my client schedule and manage appointments.
    """
) 


agent = dspy.ReAct(TamiTorReAct, tools=[book_appointment, reschedule_appointment, cancel_appointment, answer_faq])
#result = agent(request="Book an appointment for a haircut tomorrow at 3pm", context="user_name=John")
#print(result.response)
#for step, value in result.trajectory.items():
#    print(f"{step}: {value}")




for example in SEED_EXAMPLES[2:3]:
    run = run_agent_on_example(agent, example)
    print(run)
