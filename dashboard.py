# dashboard.py

import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SOC AI Operations Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: 700;
}
.sub-text {
    font-size: 18px;
    color: #6c757d;
}
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🛡 SOC AI Operations Center</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">'
    'This system ingests security tickets from Jira, processes them through an MCP server, '
    'and applies AI-driven agents to analyze patterns, risk levels, and operational bottlenecks.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- ARCHITECTURE FLOW ----------------
st.markdown('<div class="section-title">🔄 System Pipeline</div>', unsafe_allow_html=True)

st.info("""
Jira (Security Events & SOC Alerts)  
        ↓  
MCP Server (Centralized Ticket API Layer)  
        ↓  
AI Agents (Pattern Detection, Risk Scoring, Recommendation Engine)  
        ↓  
Interactive Dashboard (Visualization & Decision Support)
""")

st.markdown("""
**What this means:**
- Jira captures raw SOC security alerts.
- The MCP server exposes structured ticket data.
- AI agents analyze ticket sentences, priorities, and status.
- The dashboard transforms that analysis into operational intelligence.
""")

st.markdown("---")

# ---------------- FETCH DATA ----------------
MCP_URL = "http://34.207.86.13:8000/tickets"

@st.cache_data(ttl=120)
def get_tickets():
    try:
        resp = requests.get(MCP_URL)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Unable to fetch MCP tickets: {e}")
        return []

tickets = get_tickets()
if not tickets:
    st.stop()

df = pd.DataFrame(tickets)

# ---------------- KPI METRICS ----------------
st.markdown('<div class="section-title">📈 Operational Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", len(df))
col2.metric("Unique Alert Types", df["summary"].nunique() if "summary" in df.columns else 0)
col3.metric("High Priority", df[df["priority"].str.lower() == "high"].shape[0] if "priority" in df.columns else 0)
col4.metric("Open Tickets", df[df["status"].str.lower() != "done"].shape[0] if "status" in df.columns else 0)

st.markdown("---")

# ---------------- DISTRIBUTIONS ----------------
st.markdown('<div class="section-title">📊 Ticket Intelligence</div>', unsafe_allow_html=True)

colA, colB = st.columns(2)

if "priority" in df.columns:
    fig_priority = px.pie(df, names="priority", title="Priority Distribution")
    colA.plotly_chart(fig_priority, use_container_width=True)

if "status" in df.columns:
    status_counts = df["status"].value_counts().reset_index()
    fig_status = px.bar(
        status_counts,
        x="index",
        y="status",
        labels={"index": "Status", "status": "Count"},
        title="Status Distribution"
    )
    colB.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# ---------------- AI PATTERN AGENT ----------------
st.markdown('<div class="section-title">🤖 AI Pattern Analysis Agent</div>', unsafe_allow_html=True)

st.write("""
This agent analyzes ticket summaries at the sentence level to detect repetition,
recurring incidents, or similar alert behavior.
""")

if "summary" in df.columns:
    summary_counts = df["summary"].value_counts()
    repeated = summary_counts[summary_counts > 1]

    if repeated.empty:
        st.success("No repeated alert sentences detected.")
    else:
        st.warning("Repeated Alert Patterns:")
        for summary, count in repeated.items():
            st.write(f"• '{summary}' appears {count} times")

st.markdown("---")

# ---------------- RISK AGENT ----------------
st.markdown('<div class="section-title">⚠️ AI Risk Prioritization Agent</div>', unsafe_allow_html=True)

st.write("""
This agent evaluates priority labels and ticket state to determine
which security incidents may require immediate escalation.
""")

if "priority" in df.columns:
    high_risk = df[df["priority"].str.lower().isin(["high", "critical"])]

    st.metric("High/Critical Risk Tickets", len(high_risk))

    if not high_risk.empty:
        st.dataframe(high_risk)
    else:
        st.success("No critical risk exposure at this time.")

st.markdown("---")

# ---------------- MITIGATION AGENT ----------------
st.markdown('<div class="section-title">🛠 AI Mitigation Recommendation Engine</div>', unsafe_allow_html=True)

st.write("""
Based on workload signals and risk density, this agent suggests operational adjustments.
""")

suggestions = []

if "priority" in df.columns:
    if df[df["priority"].str.lower() == "high"].shape[0] > 5:
        suggestions.append("High-priority backlog detected — consider reallocating analysts.")

if "status" in df.columns:
    if df[df["status"].str.lower() == "in progress"].shape[0] > 4:
        suggestions.append("Multiple tickets are stalled in-progress — investigate bottlenecks.")

if not suggestions:
    suggestions.append("No immediate mitigation actions recommended.")

for s in suggestions:
    st.info(s)

st.markdown("---")

# ---------------- RAW DATA ----------------
with st.expander("📋 View Raw MCP Ticket Data"):
    st.dataframe(df)
