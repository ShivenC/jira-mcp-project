import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")

# If running on EC2 and MCP server is on same machine, keep localhost
MCP_URL = "http://localhost:8000/tickets"

# Jira search endpoint (new Cloud endpoint)
JIRA_SEARCH_URL = f"{JIRA_SERVER}/rest/api/3/search/jql"

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def extract_text_from_adf(adf):
    """
    Convert Jira Atlassian Document Format (ADF)
    into plain readable text.
    """
    if not adf or "content" not in adf:
        return ""

    text_output = ""

    for block in adf.get("content", []):
        if "content" in block:
            for item in block.get("content", []):
                if item.get("type") == "text":
                    text_output += item.get("text", "")
        text_output += "\n"

    return text_output.strip()


def fetch_jira_tickets():
    payload = {
        "jql": f'project = {JIRA_PROJECT}',
        "maxResults": 5,
        "fields": [
            "key",
            "summary",
            "description",
            "priority",
            "labels",
            "status",
            "duedate"
        ]
    }

    response = requests.post(
        JIRA_SEARCH_URL,
        headers=headers,
        json=payload,
        auth=auth
    )

    response.raise_for_status()
    data = response.json()

    return data.get("issues", [])


def push_to_mcp(ticket_data):
    response = requests.post(MCP_URL, json=ticket_data)

    if response.status_code == 200:
        print(f"✅ Added {ticket_data['key']} to MCP")
    else:
        print(f"❌ Failed to add {ticket_data['key']}")
        print(response.text)

def clear_mcp():
    response = requests.delete(MCP_URL)

    if response.status_code == 200:
        print("🗑 MCP tickets cleared successfully")
    else:
        print("❌ Failed to clear MCP tickets")
        print(response.text)

def main():
    try:
        clear_mcp()
        issues = fetch_jira_tickets()
        print(f"Fetched {len(issues)} tickets from Jira")

        for issue in issues:
            fields = issue.get("fields", {})

            description_adf = fields.get("description")
            description_text = extract_text_from_adf(description_adf)

            ticket_data = {
                "key": issue.get("key"),
                "summary": fields.get("summary", ""),
                "description": description_text,
                "priority": fields.get("priority", {}).get("name", "Medium"),
                "labels": fields.get("labels", []),
                "status": fields.get("status", {}).get("name", "To Do"),
                "due_date": fields.get("duedate")
            }

            push_to_mcp(ticket_data)

    except Exception as e:
        print("❌ Error occurred:")
        print(e)


if __name__ == "__main__":
    main()
