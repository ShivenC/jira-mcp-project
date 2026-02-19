# dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import openai
from collections import Counter
import re

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="AI SOC Automation Dashboard", layout="wide")
st.title("AI-Driven SOC Automation Dashboard (MCP + Copilot Agents)")

st.markdown("""
This dashboard connects to the MCP Server hosted on AWS EC2.
It simulates AI Copilot agents that:

1. Executive Summary Agent – summarizes all SOC tickets.
2. Risk Analysis Agent – flags high-risk tickets.
3. Mitigation Agent – detects repeated attacker IPs and suggests actions.
""")

# -----------------------------
# Pull MCP Tickets
# -----------------------------
MCP_URL = "http://34.207.86.13:8000/tickets"

try:
    response = requests.get(MCP_URL)
    tickets = response.json()
    df = pd.DataFrame(tickets)
except Exception as e:
    st.error(f"Failed to connect to MCP server: {e}")
    st.stop()

if df.empty:
    st.warning("No tickets found in MCP.")
    st.stop()

st.success(f"Loaded {len(df)} tickets from MCP Server")

st.subheader("Raw MCP Tickets")
st.dataframe(df)

# -----------------------------
# Basic Metrics
# -----------------------------
st.subheader("Ticket Priority Distribution")

priority_counts = df["priority"].value_counts()
fig = px.bar(
    x=priority_counts.index,
    y=priority_counts.values,
    labels={"x": "Priority", "y": "Count"},
    title="Tickets by Priority"
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Risk Analysis Agent
# -----------------------------
st.subheader("Risk Analysis Agent Output")

high_risk = df[
    (df["priority"].str.lower() == "high") |
    (df["description"].str.contains("critical|ransomware|breach|malware", case=False, na=False))
]

st.write(f"High-Risk Tickets Detected: {len(high_risk)}")
st.dataframe(high_risk)

# -----------------------------
# Mitigation Agent
# -----------------------------
st.subheader("Mitigation Recommendation Agent Output")

# Extract IP addresses from descriptions
ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
all_ips = []

for desc in df["description"].dropna():
    matches = re.findall(ip_pattern, desc)
    all_ips.extend(matches)

ip_counts = Counter(all_ips)
repeated_ips = {ip: count for ip, count in ip_counts.items() if count > 1}

if repeated_ips:
    st.warning("Repeated Attacker IPs Detected:")
    st.write(repeated_ips)
    st.info("Recommended Action: Consider blocking repeated IPs at firewall or WAF level.")
else:
    st.success("No repeated attacker IPs detected.")

# -----------------------------
# Executive Summary Agent (AI)
# -----------------------------
st.subheader("Executive Summary Agent (AI Generated)")

if st.button("Generate AI Executive Summary"):

    openai_key = None
    if "OPENAI_API_KEY" in st.secrets:
        openai_key = st.secrets["OPENAI_API_KEY"]
    elif os.getenv("OPENAI_API_KEY"):
        openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        st.warning("No OpenAI API key found.")
    else:
        openai.api_key = openai_key

        summary_data = {
            "total_tickets": len(df),
            "priority_counts": priority_counts.to_dict(),
            "high_risk_count": len(high_risk),
            "repeated_ips": repeated_ips
        }

        prompt = f"""
        You are a SOC executive reporting analyst.
        Based on this data, write:
        1 short executive paragraph (3-4 sentences)
        Then 5 short bullet points with key insights or actions.

        Data:
        {summary_data}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            report = response.choices[0].message.content
            st.success("Executive Report Generated:")
            st.markdown(report)

        except Exception as e:
            st.error(f"AI summary failed: {e}")
