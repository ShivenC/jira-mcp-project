from jira import JIRA
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")

# Connect to Jira
options = {"server": JIRA_SERVER}
jira = JIRA(options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Test connection
project = jira.project(JIRA_PROJECT)
print("Connected successfully!")
print(project.key)
