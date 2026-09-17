import pytest
from pydantic import ValidationError

from app.schemas import TriageResult


def test_valid_triage_result():
    result = TriageResult(
        category="TECHNICAL",
        priority="HIGH",
        summary="Sensor repeatedly disconnects during operation.",
    )

    assert result.category.value == "TECHNICAL"
    assert result.priority.value == "HIGH"


def test_invalid_category():
    with pytest.raises(ValidationError):
        TriageResult(
            category="RANDOM_CATEGORY",
            priority="HIGH",
            summary="Something happened.",
        )


def test_invalid_priority():
    with pytest.raises(ValidationError):
        TriageResult(
            category="TECHNICAL",
            priority="EXTREMELY_URGENT",
            summary="Something happened.",
        )