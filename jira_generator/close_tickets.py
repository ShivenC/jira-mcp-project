import os
import random
from jira import JIRA
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

# Percentage range to move to Done (50% to 80%)
PERCENT_MIN = 50
PERCENT_MAX = 80

# Get all issues in "In Progress"
jql_in_progress = f'project = "{JIRA_PROJECT}" AND status = "In Progress"'
issues_in_progress = jira.search_issues(jql_in_progress, maxResults=False)

num_issues = len(issues_in_progress)
if num_issues == 0:
    print("No tickets found in In Progress.")
else:
    # Randomly select percentage of issues
    percent_to_move = random.randint(PERCENT_MIN, PERCENT_MAX)
    num_to_move = max(1, int(num_issues * percent_to_move / 100))
    issues_to_move = random.sample(issues_in_progress, num_to_move)

    print(f"Moving {num_to_move} out of {num_issues} tickets to Done ({percent_to_move}%).")

    # Move selected tickets to "Done"
    for issue in issues_to_move:
        # Get available transitions for the issue
        transitions = jira.transitions(issue)
        done_transition = next((t for t in transitions if t['name'].lower() == 'done'), None)

        if done_transition:
            jira.transition_issue(issue, done_transition['id'])
            print(f"Ticket {issue.key} moved to Done")
        else:
            print(f"Ticket {issue.key} has no 'Done' transition available")

print("Done moving tickets!")
