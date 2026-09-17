from app.schemas import ComplaintCreate
from app.validation import validate_complaint


def test_complete_complaint():
    complaint = ComplaintCreate(
        customer_name="Jean Muller",
        customer_email="jean@example.com",
        order_id="ORD-1001",
        product="Industrial Sensor X1",
        complaint_text="The sensor stopped working.",
    )

    result = validate_complaint(complaint)

    assert result.is_complete is True
    assert result.missing_fields == []


def test_missing_order_id():
    complaint = ComplaintCreate(
        customer_name="Jean Muller",
        customer_email="jean@example.com",
        order_id=None,
        product="Industrial Sensor X1",
        complaint_text="The sensor stopped working.",
    )

    result = validate_complaint(complaint)

    assert result.is_complete is False
    assert result.missing_fields == ["order_id"]


def test_multiple_missing_fields():
    complaint = ComplaintCreate(
        customer_name="",
        customer_email="jean@example.com",
        order_id=None,
        product="Industrial Sensor X1",
        complaint_text="",
    )

    result = validate_complaint(complaint)

    assert result.is_complete is False
    assert result.missing_fields == [
        "customer_name",
        "order_id",
        "complaint_text",
    ]


def test_whitespace_is_missing():
    complaint = ComplaintCreate(
        customer_name="   ",
        customer_email="jean@example.com",
        order_id="ORD-1001",
        product="Industrial Sensor X1",
        complaint_text="The sensor stopped working.",
    )

    result = validate_complaint(complaint)

    assert result.is_complete is False
    assert result.missing_fields == ["customer_name"]