from app.llm import triage_complaint
from app.schemas import ComplaintCreate


complaint = ComplaintCreate(
    customer_name="Laura Becker",
    customer_email="laura@example.com",
    order_id="ORD-5003",
    product="Power Unit P2",
    complaint_text=(
        "One unit started producing a burning smell during operation "
        "so we immediately disconnected it."
    ),
)


result = triage_complaint(complaint)


print("Category:", result.category.value)
print("Priority:", result.priority.value)
print("Summary:", result.summary)