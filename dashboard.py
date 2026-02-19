# dashboard.py

import streamlit as st
import pandas as pd
import requests
from collections import Counter

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="MCP SOC Ticket Dashboard",
    layout="wide"
)

st.title("MCP SOC Ticket Dashboard")
st.markdown("Displays SOC tickets from MCP server and performs local analysis.")

# -----------------------------
# MCP SERVER URL
# -----------------------------
MCP_URL = "http://34.207.86.13:8000/tickets"

# -----------------------------
# Fetch Tickets
# -----------------------------
@st.cache_data(ttl=60)
def fetch_tickets():
    try:
        response = requests.get(MCP_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch tickets: {e}")
        return []

tickets = fetch_tickets()

if not tickets:
    st.warning("No tickets found or MCP server unreachable.")
    st.stop()

df = pd.DataFrame(tickets)

st.subheader("Raw MCP Tickets")
st.dataframe(df, use_container_width=True)

st.write(f"Total Tickets: {len(df)}")

# -----------------------------
# Agent 1: Find Repeated Tickets
# -----------------------------
st.subheader("Agent 1: Repeated Ticket Detection")

if "summary" in df.columns:
    summary_counts = df["summary"].value_counts()
    repeated = summary_counts[summary_counts > 1]

    if not repeated.empty:
        st.warning("Repeated Ticket Summaries Detected:")
        for summary, count in repeated.items():
            st.write(f"- {summary} ({count} times)")
    else:
        st.success("No repeated ticket summaries found.")
else:
    st.info("No 'summary' column found in tickets.")

# -----------------------------
# Agent 2: Recommendation Engine
# -----------------------------
st.subheader("Agent 2: Automated Recommendations")

recommendations = []

if "priority" in df.columns:
    high_priority_count = df[df["priority"].str.lower() == "high"].shape[0]
    if high_priority_count > 3:
        recommendations.append("High volume of HIGH priority tickets. Consider incident escalation review.")

if "status" in df.columns:
    in_progress = df[df["status"].str.lower() == "in progress"].shape[0]
    if in_progress > 5:
        recommendations.append("Large number of tickets still in progress. Review SOC workload distribution.")

if not recommendations:
    recommendations.append("Ticket flow appears stable. Continue monitoring.")

for rec in recommendations:
    st.info(rec)

# -----------------------------
# Agent 3: Overall Summary
# -----------------------------
st.subheader("Agent 3: Overall Ticket Summary")

priority_distribution = {}
status_distribution = {}

if "priority" in df.columns:
    priority_distribution = df["priority"].value_counts().to_dict()

if "status" in df.columns:
    status_distribution = df["status"].value_counts().to_dict()

st.markdown("### Ticket Priority Distribution")
st.write(priority_distribution)

st.markdown("### Ticket Status Distribution")
st.write(status_distribution)

# -----------------------------
# Architecture Section
# -----------------------------
st.markdown("---")
st.subheader("System Architecture Overview")

st.markdown("""
This dashboard connects to an MCP server hosted on AWS EC2.

Workflow:

1. Simulated security events generate Jira tickets.
2. MCP server stores and exposes tickets via API.
3. Streamlit dashboard retrieves ticket data.
4. Local analysis agents perform:
   - Duplicate detection
   - Recommendations
   - Ticket summarization
5. GitHub Copilot Agents (via MCP integration) can also analyze the same MCP server tools inside the repository.

This project demonstrates AI-assisted SOC automation using MCP + Copilot Agents.
""")
