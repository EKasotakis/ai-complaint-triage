from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ComplaintCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_id: Optional[str] = None
    product: Optional[str] = None
    complaint_text: Optional[str] = None


class ValidationResult(BaseModel):
    is_complete: bool
    missing_fields: list[str]


class ComplaintCategory(str, Enum):
    TECHNICAL = "TECHNICAL"
    PRODUCT_QUALITY = "PRODUCT_QUALITY"
    DELIVERY = "DELIVERY"
    BILLING = "BILLING"
    OTHER = "OTHER"


class ComplaintPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TriageResult(BaseModel):
    category: ComplaintCategory
    priority: ComplaintPriority
    summary: str


class ComplaintResponse(BaseModel):
    case_id: str
    is_complete: bool
    missing_fields: list[str]
    status: str

    category: ComplaintCategory | None = None
    priority: ComplaintPriority | None = None
    summary: str | None = None
    assigned_team: str | None = None

    submitted_at: datetime
    processed_at: datetime | None = None


class MetricsResponse(BaseModel):
    total_complaints: int
    triaged_complaints: int
    incomplete_complaints: int
    ai_failed_complaints: int

    completion_rate: float
    automation_rate: float
    ai_failure_rate: float
    average_processing_time_seconds: float

    category_breakdown: dict[str, int]
    priority_breakdown: dict[str, int]
    team_breakdown: dict[str, int]