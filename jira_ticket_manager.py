from jira_config import JiraConfig
import json

class JiraTicketManager:
    def __init__(self):
        self.config = JiraConfig()
        self.jira = self.config.get_jira_client()

    def get_ticket(self, ticket_key):
        try:
            issue = self.jira.issue(ticket_key)
            return self._format_ticket_info(issue)
        except Exception as e:
            print(f"チケット取得エラー: {e}")
            return None

    def search_tickets(self, jql_query, max_results=50):
        try:
            issues = self.jira.search_issues(jql_query, maxResults=max_results)
            return [self._format_ticket_info(issue) for issue in issues]
        except Exception as e:
            print(f"チケット検索エラー: {e}")
            return []

    def get_tickets_by_project(self, project_key, max_results=50):
        jql = f"project = {project_key}"
        return self.search_tickets(jql, max_results)

    def get_tickets_by_assignee(self, assignee, max_results=50):
        jql = f"assignee = '{assignee}'"
        return self.search_tickets(jql, max_results)

    def get_tickets_by_status(self, status, max_results=50):
        jql = f"status = '{status}'"
        return self.search_tickets(jql, max_results)

    def _format_ticket_info(self, issue):
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description,
            'status': issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
            'created': str(issue.fields.created),
            'updated': str(issue.fields.updated),
            'priority': issue.fields.priority.name if issue.fields.priority else None,
            'issue_type': issue.fields.issuetype.name,
            'project': issue.fields.project.key
        }

    def export_to_json(self, tickets, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, ensure_ascii=False, indent=2)
            print(f"データを {filename} にエクスポートしました")
        except Exception as e:
            print(f"エクスポートエラー: {e}")

def main():
    manager = JiraTicketManager()

    print("=== Jira接続テスト ===")
    if not manager.config.test_connection():
        return

    print("\n=== チケット取得例 ===")

    # 特定のチケットを取得
    ticket_key = input("チケットキーを入力してください (例: PROJECT-123): ")
    if ticket_key:
        ticket = manager.get_ticket(ticket_key)
        if ticket:
            print(f"\nチケット情報:")
            print(json.dumps(ticket, ensure_ascii=False, indent=2))

    # プロジェクトのチケット一覧を取得
    project_key = input("\nプロジェクトキーを入力してください (例: PROJECT): ")
    if project_key:
        tickets = manager.get_tickets_by_project(project_key, 10)
        print(f"\n{project_key}プロジェクトのチケット数: {len(tickets)}")

        if tickets:
            print("\nチケット一覧:")
            for ticket in tickets[:5]:  # 最初の5件を表示
                print(f"- {ticket['key']}: {ticket['summary']} [{ticket['status']}]")

            # JSONファイルにエクスポート
            manager.export_to_json(tickets, f"{project_key}_tickets.json")

if __name__ == "__main__":
    main()