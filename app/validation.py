from app.schemas import ComplaintCreate, ValidationResult


REQUIRED_FIELDS = [
    "customer_name",
    "customer_email",
    "order_id",
    "product",
    "complaint_text",
]


def validate_complaint(complaint: ComplaintCreate) -> ValidationResult:
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = getattr(complaint, field)

        if value is None or not value.strip():
            missing_fields.append(field)

    return ValidationResult(
        is_complete=len(missing_fields) == 0,
        missing_fields=missing_fields,
    )