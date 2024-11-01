import datetime
import os
from dataclasses import dataclass
from math import floor

import requests
from requests.auth import HTTPBasicAuth

JIRA_API_URL = 'https://maddevs.atlassian.net'
JIRA_EMAIL = 'kirill.a@maddevs.io'
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
STATUSES = ['In Progress', 'Under Review', 'In Testing', 'To do', 'IN PROGRESS']
JQL_QUERY = (f'status IN (' +
             ", ".join(["'" + status + "'" for status in STATUSES]) +
             ')'
             f'AND assignee = currentUser() '
             # f'AND (type IN ["Sub-task", "Task"]'
             )
JIRA_SEARCH_URL = f'{JIRA_API_URL}/rest/api/2/search'


@dataclass
class Task:
    external_id: str
    description: str
    brief: str

    def to_dict(self):
        return {
            'external_id': self.external_id,
            'description': self.description,
            'brief': self.brief
        }

    def to_string(self):
        return f'{self.external_id} - {self.brief}'


def get_tasks_in_statuses(prefix=None):
    headers = {
        'Content-Type': 'application/json',
    }
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    # Prepare the query parameters
    params = {
        'jql': JQL_QUERY,
        'maxResults': 100,  # Adjust the number of results as needed
    }

    # Make the request to the Jira API
    response = requests.get(JIRA_SEARCH_URL, headers=headers, params=params, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        issues = response.json().get('issues', [])
        tasks = [
            Task(
                external_id=issue.get('key'),
                brief=issue['fields'].get('summary', ''),
                description=issue['fields'].get('description', '')
            )
            for issue in issues
            if prefix is None or issue.get('key').startswith(prefix)
        ]
        return tasks
    else:
        print(f"Failed to retrieve tasks: {response.status_code} - {response.text}")
        return []


def create_jira_worklog(issue_key, description, time_spent_seconds, start_time: datetime.datetime):
    url = f"{JIRA_API_URL}/rest/api/2/issue/{issue_key}/worklog"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Content-Type": "application/json"}
    start_time = start_time.astimezone(tz=datetime.timezone.utc)
    data = {
        "comment": description,
        "started": start_time.strftime('%Y-%m-%dT%H:%M:%S.000%z'),
        "timeSpentSeconds": int(floor(time_spent_seconds)),
    }
    response = requests.post(url, json=data, headers=headers, auth=auth)
    return response
    # return None
