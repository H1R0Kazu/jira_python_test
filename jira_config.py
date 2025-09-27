import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

class JiraConfig:
    def __init__(self):
        self.url = os.getenv('JIRA_URL')
        self.username = os.getenv('JIRA_USERNAME')
        self.api_token = os.getenv('JIRA_API_TOKEN')

        if not all([self.url, self.username, self.api_token]):
            raise ValueError("JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN must be set in environment variables")

    def get_jira_client(self):
        auth = (self.username, self.api_token)
        options = {
            'server': self.url,
            'rest_api_version': '3',
            'agile_rest_api_version': '1.0'
        }
        return JIRA(options=options, basic_auth=auth)

    def test_connection(self):
        try:
            jira = self.get_jira_client()
            user = jira.current_user()
            print(f"接続成功: {user}")
            return True
        except Exception as e:
            print(f"接続失敗: {e}")
            return False