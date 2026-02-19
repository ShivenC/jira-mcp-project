# dashboard.py

import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# ---- Page Setup ----
st.set_page_config(
    page_title="SOC Ticket Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 SOC Ticket Intelligence Dashboard")
st.markdown("""
Visual analytics and agent-driven insights from your MCP Server.
Powered by ticket ingestion from Jira → MCP → Intelligent analysis.
""")

# ---- Fetch MCP Tickets ----
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

# ---- KPI SUMMARY ----
st.markdown("## 📈 Key Ticket Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", len(df))
col2.metric("Unique Ticket Types", df["summary"].nunique() if "summary" in df.columns else 0)
col3.metric("High Priority Count", df[df["priority"].str.lower() == "high"].shape[0] if "priority" in df.columns else 0)
col4.metric("Open Tickets", df[df["status"].str.lower() != "done"].shape[0] if "status" in df.columns else 0)

st.markdown("---")

# ----RAW TICKET TABLE----
with st.expander("📋 Raw Ticket Data"):
    st.dataframe(df)

# ---- DISTRIBUTION CHARTS ----
st.markdown("## 📊 Ticket Distributions")

fig_priority = None
if "priority" in df.columns:
    fig_priority = px.pie(
        df, names="priority",
        title="Priority Breakdown"
    )

fig_status = None
if "status" in df.columns:
    fig_status = px.bar(
        df["status"].value_counts().reset_index(),
        x="index",
        y="status",
        labels={"index": "Status", "status": "Count"},
        title="Ticket Status Distribution"
    )

colA, colB = st.columns(2)
if fig_priority:
    colA.plotly_chart(fig_priority, use_container_width=True)
if fig_status:
    colB.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# ---- REPEATED PATTERNS AGENT ----
with st.expander("🔍 Repeated Patterns Agent"):
    st.write("Detects repeated ticket summaries or repeated characteristics")

    if "summary" in df.columns:
        summary_counts = df["summary"].value_counts()
        repeated = summary_counts[summary_counts > 1]

        if repeated.empty:
            st.info("No repeated ticket summaries found.")
        else:
            for summary, count in repeated.items():
                st.warning(f"• **{summary}** appears {count} times")
    else:
        st.text("No 'summary' field available for pattern detection.")

# ---- RISK ANALYSIS AGENT ----
with st.expander("⚠️ Risk Analysis Agent"):
    st.write("Highlights tickets that may need urgent attention")

    if "priority" in df.columns:
        high_risk = df[df["priority"].str.lower().isin(["high", "critical"])]
        st.markdown(f"**High/Critical risk tickets:** {len(high_risk)}")

        if not high_risk.empty:
            st.dataframe(high_risk)
        else:
            st.success("No high-risk tickets right now.")
    else:
        st.text("Priority field missing — cannot assess risk.")

# ---- MITIGATION RECOMMENDER AGENT ----
with st.expander("🛠 Mitigation Recommendation Agent"):
    st.write("Suggests actions based on patterns and risk signals")

    suggestions = []

    # Simple prioritization rule example
    if "priority" in df.columns:
        high_count = df[df["priority"].str.lower() == "high"].shape[0]
        if high_count > 5:
            suggestions.append("Review SOC workload — >5 high priority tickets.")

    if "status" in df.columns:
        stuck = df[df["status"].str.lower() == "in progress"].shape[0]
        if stuck > 4:
            suggestions.append("Consider redistributing tickets stuck in progress.")

    if not suggestions:
        suggestions.append("No automated recommendations at this time — monitor ticket flow.")

    for s in suggestions:
        st.info(f"🔹 {s}")

st.markdown("---")

# ---- ARCHITECTURE NOTES ----
st.markdown("## 🏗 Architecture")

st.markdown("""
This dashboard presents SOC tickets collected via the Model Context Protocol (MCP) server.

**Flow:**
1. Jira captures SOC events.
2. MCP Server ingests and exposes ticket data.
3. Dashboard visualizes the ticket stream.
4. Local agents provide:
   - Pattern detection
   - Risk prioritization
   - Mitigation guidance

**Future:**
With GitHub Copilot Coding Agent MCP integration,
the same MCP tools can be autonomously queried for:
- PR-based reporting
- Automated insights
- Scheduled analysis workflows
""")
