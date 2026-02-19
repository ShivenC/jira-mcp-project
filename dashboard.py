import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="SOC Command Center",
    layout="wide"
)

# ===============================
# DARK THEME + CUSTOM FONT
# ===============================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #0f172a;
        color: #e2e8f0;
    }

    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 12px;
    }

    h1, h2, h3 {
        color: #38bdf8;
    }

    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# TITLE
# ===============================
st.title("🛡 SOC Command Center")
st.markdown("Real-time analytics from Jira → MCP Server → AI Agents")

# ===============================
# FETCH MCP DATA
# ===============================
MCP_URL = "http://34.207.86.13:8000/tickets"

try:
    response = requests.get(MCP_URL, timeout=5)
    tickets = response.json()
    df = pd.DataFrame(tickets)
except Exception as e:
    st.error(f"Failed to connect to MCP server: {e}")
    st.stop()

if df.empty:
    st.warning("No tickets found in MCP.")
    st.stop()

# ===============================
# METRICS
# ===============================
st.subheader("📊 Live SOC Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", len(df))
col2.metric("Unique Priorities", df["priority"].nunique())
col3.metric("High Priority", (df["priority"] == "High").sum())
col4.metric("Open Tickets", (df["status"] == "In Progress").sum())

# ===============================
# RAW DATA
# ===============================
st.subheader("📋 Active Ticket Feed")
st.dataframe(df, use_container_width=True)

# ===============================
# VISUAL ANALYTICS
# ===============================
st.subheader("📈 Operational Intelligence")

# ---- Priority Distribution ----
priority_counts = df["priority"].value_counts().reset_index()
priority_counts.columns = ["priority", "count"]

fig_priority = px.bar(
    priority_counts,
    x="priority",
    y="count",
    title="Ticket Priority Distribution"
)

st.plotly_chart(fig_priority, use_container_width=True)

# ---- Status Distribution (FIXED ERROR HERE) ----
status_counts = df["status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]

fig_status = px.bar(
    status_counts,
    x="status",
    y="count",
    title="Ticket Status Distribution"
)

st.plotly_chart(fig_status, use_container_width=True)

# ===============================
# AGENT SIMULATION OUTPUT
# ===============================
st.subheader("🤖 AI Agent Insights")

# Executive Summary Agent
with st.expander("Executive Summary Agent"):
    summary = (
        f"There are currently {len(df)} active SOC tickets. "
        f"{(df['priority'] == 'High').sum()} are marked as High priority. "
        f"Most common status: {df['status'].value_counts().idxmax()}."
    )
    st.write(summary)

# Risk Agent
with st.expander("Risk Analysis Agent"):
    high_risk = df[df["priority"] == "High"]
    if not high_risk.empty:
        st.warning("High-risk tickets detected:")
        st.dataframe(high_risk)
    else:
        st.success("No high-risk tickets detected.")

# Mitigation Agent
with st.expander("Mitigation Recommendation Agent"):
    if "description" in df.columns:
        repeated_ips = df["description"].str.extract(r'(\\d+\\.\\d+\\.\\d+\\.\\d+)')[0]
        ip_counts = repeated_ips.value_counts()
        flagged_ips = ip_counts[ip_counts > 1]

        if not flagged_ips.empty:
            st.error("Repeated attacker IPs detected:")
            st.write(flagged_ips)
            st.info("Recommended Action: Block repeated IP addresses at firewall.")
        else:
            st.success("No repeated attacker IPs found.")
    else:
        st.info("No description field available for IP analysis.")
