from ollama import chat

from app.schemas import ComplaintCreate, TriageResult


class LLMError(Exception):
    """Raised when complaint triage with the local LLM fails."""
    pass





MODEL_NAME = "qwen3:4b"


TRIAGE_INSTRUCTIONS = """
You are a customer complaint triage assistant for an industrial equipment company.

Classify the complaint using exactly one of these categories:

TECHNICAL:
Software, firmware, connectivity, configuration, sensor readings,
error codes, or functional technical problems.

PRODUCT_QUALITY:
Physical defects, damaged products, manufacturing defects,
cracks, broken components, or physical product damage.

DELIVERY:
Late deliveries, missing shipments, incorrect quantities,
or missing items.

BILLING:
Invoices, duplicate charges, incorrect charges,
billing addresses, or payment-related issues.

OTHER:
Cases that do not fit the categories above.

Assign exactly one priority:

LOW:
Routine request with little or no operational impact.

MEDIUM:
Normal complaint requiring attention but without major business impact.

HIGH:
Significant operational impact, repeated failures,
or inability to use important equipment.

CRITICAL:
Immediate safety risk, dangerous equipment behavior,
or a production-stopping incident.

Write a short factual summary.

Do not invent information that is not present in the complaint.
"""


def triage_complaint(complaint: ComplaintCreate) -> TriageResult:
    complaint_content = f"""
Product: {complaint.product}
Complaint: {complaint.complaint_text}
"""

    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": TRIAGE_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": complaint_content,
                },
            ],
            format=TriageResult.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        return TriageResult.model_validate_json(
            response.message.content
        )

    except Exception as error:
        raise LLMError("LLM triage failed.") from error