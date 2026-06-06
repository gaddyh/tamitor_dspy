import uuid

def book_appointment(service: str, date: str, time: str, customer_name: str):
    missing = []

    if not service:
        missing.append("service")
    if not date:
        missing.append("date")
    if not time:
        missing.append("time")
    if not customer_name:
        missing.append("customer_name")

    return {
        "tool": "book_appointment",
        "args": {
            "service": service,
            "date": date,
            "time": time,
            "customer_name": customer_name,
        },
        "missing": missing,
        "status": "called_with_missing_args" if missing else "called",
    }

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

def handoff_to_human():
    res = "Handing off to human"
    print(res)
    return res

def get_active_bookings(customer_name: str) -> dict:
    """
    Fetch active future bookings for a customer.

    Required args:
    - customer_name

    Returns:
    - appointment_id
    - service
    - date
    - time
    """
    res = f"Active bookings for {customer_name}"
    print(res)
    return res