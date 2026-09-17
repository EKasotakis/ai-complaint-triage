from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Complaint
from app.schemas import (
    ComplaintCreate,
    ComplaintResponse,
    MetricsResponse,
)
from app.validation import validate_complaint
from app.llm import LLMError, triage_complaint
from app.routing import route_complaint



app = FastAPI(
    title="AI Customer Complaint & Triage System",
    description="API for validating, classifying and routing customer complaints.",
    version="1.0.0",
)

 
@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/complaints", response_model=ComplaintResponse)
def submit_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
):
    submitted_at = datetime.utcnow()

    validation = validate_complaint(complaint)

    current_count = db.query(func.count(Complaint.id)).scalar()
    case_id = f"C{current_count + 1:06d}"

    # Incomplete complaints are stored without AI processing.
    if not validation.is_complete:
        db_complaint = Complaint(
            case_id=case_id,
            customer_name=complaint.customer_name,
            customer_email=complaint.customer_email,
            order_id=complaint.order_id,
            product=complaint.product,
            complaint_text=complaint.complaint_text,
            is_complete=False,
            status="INCOMPLETE",
            submitted_at=submitted_at,
        )

        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)

        return ComplaintResponse(
            case_id=db_complaint.case_id,
            is_complete=False,
            missing_fields=validation.missing_fields,
            status=db_complaint.status,
            category=None,
            priority=None,
            summary=None,
            assigned_team=None,
            submitted_at=db_complaint.submitted_at,
            processed_at=None,
        )

    # Complete complaints are analyzed by the local LLM.
    try:
        triage = triage_complaint(complaint)

    except LLMError:
        db_complaint = Complaint(
            case_id=case_id,
            customer_name=complaint.customer_name,
            customer_email=complaint.customer_email,
            order_id=complaint.order_id,
            product=complaint.product,
            complaint_text=complaint.complaint_text,
            is_complete=True,
            status="AI_FAILED",
            submitted_at=submitted_at,
        )

        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)

        return ComplaintResponse(
            case_id=db_complaint.case_id,
            is_complete=True,
            missing_fields=[],
            status=db_complaint.status,
            category=None,
            priority=None,
            summary=None,
            assigned_team=None,
            submitted_at=db_complaint.submitted_at,
            processed_at=None,
        )

    assigned_team = route_complaint(triage.category)

    processed_at = datetime.utcnow()

    db_complaint = Complaint(
        case_id=case_id,
        customer_name=complaint.customer_name,
        customer_email=complaint.customer_email,
        order_id=complaint.order_id,
        product=complaint.product,
        complaint_text=complaint.complaint_text,
        is_complete=True,
        status="TRIAGED",
        category=triage.category.value,
        priority=triage.priority.value,
        summary=triage.summary,
        assigned_team=assigned_team,
        submitted_at=submitted_at,
        processed_at=processed_at,
    )

    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)

    return ComplaintResponse(
        case_id=db_complaint.case_id,
        is_complete=True,
        missing_fields=[],
        status=db_complaint.status,
        category=triage.category,
        priority=triage.priority,
        summary=db_complaint.summary,
        assigned_team=db_complaint.assigned_team,
        submitted_at=db_complaint.submitted_at,
        processed_at=db_complaint.processed_at,
    )


@app.get("/complaints")
def get_complaints(
    db: Session = Depends(get_db),
):
    complaints = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "case_id": complaint.case_id,
            "status": complaint.status,
            "category": complaint.category,
            "priority": complaint.priority,
            "assigned_team": complaint.assigned_team,
            "summary": complaint.summary,
            "submitted_at": complaint.submitted_at,
        }
        for complaint in complaints
    ]


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):

    total = db.query(func.count(Complaint.id)).scalar()

    triaged = (
        db.query(func.count(Complaint.id))
        .filter(Complaint.status == "TRIAGED")
        .scalar()
    )

    incomplete = (
        db.query(func.count(Complaint.id))
        .filter(Complaint.status == "INCOMPLETE")
        .scalar()
    )

    ai_failed = (
        db.query(func.count(Complaint.id))
        .filter(Complaint.status == "AI_FAILED")
        .scalar()
    )

    complete = total - incomplete

    completion_rate = (
        complete / total * 100
        if total > 0
        else 0.0
    )

    automation_rate = (
        triaged / total * 100
        if total > 0
        else 0.0
    )

    ai_failure_rate = (
        ai_failed / complete * 100
        if complete > 0
        else 0.0
    )

    category_rows = (
    db.query(
        Complaint.category,
        func.count(Complaint.id),
    )
        .filter(Complaint.category.isnot(None))
        .group_by(Complaint.category)
        .all()
    )

    category_breakdown = {
        category: count
        for category, count in category_rows
    }

    priority_rows = (
    db.query(
        Complaint.priority,
        func.count(Complaint.id),
    )
    .filter(Complaint.priority.isnot(None))
    .group_by(Complaint.priority)
    .all()
    )

    priority_breakdown = {
        priority: count
        for priority, count in priority_rows
    }


    team_rows = (
        db.query(
            Complaint.assigned_team,
            func.count(Complaint.id),
        )
        .filter(Complaint.assigned_team.isnot(None))
        .group_by(Complaint.assigned_team)
        .all()
    )

    team_breakdown = {
        team: count
        for team, count in team_rows
    }

    triaged_cases = (
    db.query(Complaint)
    .filter(
        Complaint.status == "TRIAGED",
        Complaint.processed_at.isnot(None),
    )
    .all()
    )

    processing_times = [
    (case.processed_at - case.submitted_at).total_seconds()
    for case in triaged_cases
    ]

    average_processing_time = (
        sum(processing_times) / len(processing_times)
        if processing_times
        else 0.0
    )

    return MetricsResponse(
    total_complaints=total,
    triaged_complaints=triaged,
    incomplete_complaints=incomplete,
    ai_failed_complaints=ai_failed,

    completion_rate=round(completion_rate, 2),
    automation_rate=round(automation_rate, 2),
    ai_failure_rate=round(ai_failure_rate, 2),

    category_breakdown=category_breakdown,
    priority_breakdown=priority_breakdown,
    team_breakdown=team_breakdown,
    average_processing_time_seconds=round(
    average_processing_time,
    2,
    ),
)