import os
import random
from datetime import datetime, timedelta
from jira import JIRA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")

# Connect to Jira
jira = JIRA(
    options={"server": JIRA_SERVER},
    basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
)

# Repeated attacker IPs (these will show up often)
repeat_attackers = [
    "185.243.115.84",
    "45.33.21.9",
    "103.77.192.11"
]

fake_analysts = [
    "Alice Chen", "Bob Patel", "Carlos Ruiz", "Dana Smith",
    "Ethan Lee", "Fatima Khan", "George Li", "Hannah Park"
]

countries = [
    "USA", "Germany", "India", "Brazil",
    "Japan", "Canada", "UK", "Australia"
]

event_types = [
    "Failed Login",
    "Malware Execution",
    "Port Scan",
    "Privilege Escalation",
    "Data Exfiltration"
]

severities = ["Low", "Medium", "High", "Critical"]

priorities = ["Highest", "High", "Medium", "Low"]
labels = ["security", "incident", "alert"]

# Generate random IP
def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def generate_ticket():
    # 40% chance of repeated malicious IP
    if random.random() < 0.4:
        src_ip = random.choice(repeat_attackers)
    else:
        src_ip = random_ip()

    dst_ip = random_ip()
    src_country = random.choice(countries)
    severity = random.choice(severities)
    event_type = random.choice(event_types)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    analyst = random.choice(fake_analysts)

    description = f"""
SOC_EVENT_LOG

SRC_IP: {src_ip}
DST_IP: {dst_ip}
COUNTRY: {src_country}
SEVERITY: {severity}
EVENT_TYPE: {event_type}
TIMESTAMP: {timestamp}
ANALYST: {analyst}
"""

    ticket_dict = {
        "project": {"key": JIRA_PROJECT},
        "summary": "SOC Event Alert",
        "description": description,
        "issuetype": {"name": "Task"},
        "priority": {"name": random.choice(priorities)},
        "labels": random.sample(labels, k=1),
        "duedate": (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    }

    return ticket_dict


def create_tickets(n):
    for _ in range(n):
        ticket = generate_ticket()
        issue = jira.create_issue(**ticket)

        # Move ALL tickets to In Progress
        transitions = jira.transitions(issue)
        for t in transitions:
            if t["name"] == "In Progress":
                jira.transition_issue(issue, t["id"])
                break

        print(f"Created {issue.key} -> In Progress")


if __name__ == "__main__":
    num_tickets = random.randint(50, 100)
    print(f"Creating {num_tickets} SOC tickets...")
    create_tickets(num_tickets)
