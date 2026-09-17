import requests
import streamlit as st
import pandas as pd
import plotly.express as px


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Complaint Triage Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("AI Customer Complaint & Triage Dashboard")

st.write(
    "Operational monitoring of customer complaint validation, "
    "AI triage and routing."
)


def load_metrics():
    response = requests.get(
        f"{API_URL}/metrics",
        timeout=5,
    )
    response.raise_for_status()

    return response.json()


def load_complaints():
    response = requests.get(
        f"{API_URL}/complaints",
        timeout=5,
    )
    response.raise_for_status()

    return response.json()


try:
    metrics = load_metrics()
    complaints = load_complaints()


except requests.RequestException:
    st.error(
        "Could not connect to the complaint triage API. "
        "Make sure FastAPI is running."
    )
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Complaints",
    metrics["total_complaints"],
)

col2.metric(
    "Completion Rate",
    f'{metrics["completion_rate"]:.1f}%',
)

col3.metric(
    "Automation Rate",
    f'{metrics["automation_rate"]:.1f}%',
)

col4.metric(
    "AI Failure Rate",
    f'{metrics["ai_failure_rate"]:.1f}%',
)

col5.metric(
    "Avg. Triage Time",
    f'{metrics["average_processing_time_seconds"]:.2f} s',
)

st.subheader("Processing Status")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Successfully Triaged",
    metrics["triaged_complaints"],
)

col2.metric(
    "Incomplete",
    metrics["incomplete_complaints"],
)

col3.metric(
    "AI Failed",
    metrics["ai_failed_complaints"],
)

st.subheader("Complaint Analysis")

category_data = pd.DataFrame(
    metrics["category_breakdown"].items(),
    columns=["Category", "Complaints"],
)

category_chart = px.bar(
    category_data,
    x="Category",
    y="Complaints",
    title="Complaints by Category",
)

st.plotly_chart(
    category_chart,
    use_container_width=True,
)

priority_data = pd.DataFrame(
    metrics["priority_breakdown"].items(),
    columns=["Priority", "Complaints"],
)

priority_chart = px.bar(
    priority_data,
    x="Priority",
    y="Complaints",
    title="Complaints by Priority",
)

st.plotly_chart(
    priority_chart,
    use_container_width=True,
)

team_data = pd.DataFrame(
    metrics["team_breakdown"].items(),
    columns=["Team", "Complaints"],
)

team_chart = px.bar(
    team_data,
    x="Team",
    y="Complaints",
    title="Complaints by Assigned Team",
)

st.plotly_chart(
    team_chart,
    use_container_width=True,
)

st.subheader("Recent Complaints")

complaints_df = pd.DataFrame(complaints)

complaints_df = complaints_df.rename(
    columns={
        "case_id": "Case ID",
        "status": "Status",
        "category": "Category",
        "priority": "Priority",
        "assigned_team": "Assigned Team",
        "summary": "AI Summary",
        "submitted_at": "Submitted At",
    }
)

st.dataframe(
    complaints_df,
    use_container_width=True,
    hide_index=True,
)