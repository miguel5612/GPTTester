import os
import requests


class JiraIntegration:
    """Simple Jira REST API client for basic operations."""

    def __init__(self) -> None:
        self.base_url = os.getenv("JIRA_BASE_URL", "")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
        if self.base_url and not self.base_url.endswith("/"):
            self.base_url += "/"

    def _auth(self) -> tuple[str, str]:
        if not self.email or not self.api_token:
            raise RuntimeError("Jira credentials not configured")
        return self.email, self.api_token

    def create_issue(self, summary: str, description: str | None = None) -> dict:
        url = f"{self.base_url}rest/api/2/issue"
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description or "",
                "issuetype": {"name": "Task"},
            }
        }
        response = requests.post(url, json=payload, auth=self._auth(), timeout=10)
        response.raise_for_status()
        return response.json()

    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        url = f"{self.base_url}rest/api/2/issue/{issue_key}/transitions"
        payload = {"transition": {"id": transition_id}}
        response = requests.post(url, json=payload, auth=self._auth(), timeout=10)
        response.raise_for_status()
        return True

    def trigger_pipeline(self, pipeline_url: str) -> bool:
        response = requests.post(pipeline_url, auth=self._auth(), timeout=10)
        response.raise_for_status()
        return True
