
from ..agents.schemas import DatasetExample

SEED_EXAMPLES = [
    DatasetExample(
        id="book_complete_001",
        category="complete_booking",
        request="Book an appointment for a haircut tomorrow at 3pm",
        context="user_name=John",
        expected_behavior="tool_call",
        expected_tool="book_appointment",
        expected_args={
            "service": "haircut",
            "date": "tomorrow",
            "time": "3pm",
            "customer_name": "John",
        },
        missing_args=[],
        forbidden_tools=[],
        notes="Complete booking. Name comes from context.",
    ),

    DatasetExample(
        id="book_missing_service_001",
        category="incomplete_booking",
        request="Book an appointment tomorrow at 3pm",
        context="user_name=John",
        expected_behavior="clarify",
        expected_tool=None,
        expected_args={
            "date": "tomorrow",
            "time": "3pm",
            "customer_name": "John",
        },
        missing_args=["service"],
        forbidden_tools=["book_appointment"],
        notes="Booking intent exists, but service is missing.",
    ),

    DatasetExample(
        id="book_missing_time_001",
        category="incomplete_booking",
        request="Book a haircut tomorrow",
        context="user_name=John",
        expected_behavior="clarify",
        expected_tool=None,
        expected_args={
            "service": "haircut",
            "date": "tomorrow",
            "customer_name": "John",
        },
        missing_args=["time"],
        forbidden_tools=["book_appointment"],
        notes="Booking intent exists, but time is missing.",
    ),

    DatasetExample(
        id="book_missing_name_001",
        category="incomplete_booking",
        request="Book a haircut tomorrow at 3pm",
        context="",
        expected_behavior="clarify",
        expected_tool=None,
        expected_args={
            "service": "haircut",
            "date": "tomorrow",
            "time": "3pm",
        },
        missing_args=["customer_name"],
        forbidden_tools=["book_appointment"],
        notes="No user name in request or context.",
    ),

    DatasetExample(
        id="reschedule_complete_001",
        category="reschedule",
        request="Move appointment abc123 to tomorrow at 5pm",
        context="user_name=John",
        expected_behavior="tool_call",
        expected_tool="reschedule_appointment",
        expected_args={
            "appointment_id": "abc123",
            "date": "tomorrow",
            "time": "5pm",
        },
        missing_args=[],
        forbidden_tools=[],
        notes="Existing appointment is identified and new time is provided.",
    ),

    DatasetExample(
        id="reschedule_missing_existing_001",
        category="reschedule",
        request="Can I move my appointment to tomorrow at 5pm?",
        context="user_name=John",
        expected_behavior="clarify",
        expected_tool=None,
        expected_args={
            "date": "tomorrow",
            "time": "5pm",
        },
        missing_args=["appointment_id"],
        forbidden_tools=["reschedule_appointment"],
        notes="Cannot reschedule without identifying existing appointment.",
    ),

    DatasetExample(
        id="cancel_complete_001",
        category="cancel",
        request="Cancel appointment abc123",
        context="user_name=John",
        expected_behavior="tool_call",
        expected_tool="cancel_appointment",
        expected_args={
            "appointment_id": "abc123",
        },
        missing_args=[],
        forbidden_tools=[],
        notes="Cancellation with explicit appointment id.",
    ),

    DatasetExample(
        id="cancel_missing_existing_001",
        category="cancel",
        request="Cancel my appointment",
        context="user_name=John",
        expected_behavior="clarify",
        expected_tool=None,
        expected_args={},
        missing_args=["appointment_id"],
        forbidden_tools=["cancel_appointment"],
        notes="Cannot cancel without identifying which appointment.",
    ),

    DatasetExample(
        id="faq_price_001",
        category="faq",
        request="How much does a facial cost?",
        context="user_name=John",
        expected_behavior="tool_call",
        expected_tool="answer_faq",
        expected_args={
            "topic": "facial price",
        },
        missing_args=[],
        forbidden_tools=["book_appointment"],
        notes="FAQ should not become a booking flow.",
    ),
]