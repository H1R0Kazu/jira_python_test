from jira_config import JiraConfig
import json
import requests

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

    def search_tickets_v3(self, jql_query, max_results=50):
        try:
            url = f"{self.config.url}/rest/api/3/search/jql"
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            auth = (self.config.username, self.config.api_token)

            payload = {
                'jql': jql_query,
                'maxResults': max_results,
                'fields': ['*all']
            }

            response = requests.post(url, json=payload, headers=headers, auth=auth)
            response.raise_for_status()

            data = response.json()
            issues = data.get('issues', [])

            print(f"検索結果: {len(issues)}件のチケットが見つかりました")

            all_tickets = []
            subtask_count = 0

            for issue_data in issues:
                # JIRAオブジェクト風に変換 - ネストしたオブジェクトも適切に処理
                fields_data = issue_data['fields']

                # ネストしたオブジェクトを適切に変換
                def convert_nested_object(data):
                    if isinstance(data, dict):
                        obj = type('Object', (), {})()
                        for key, value in data.items():
                            setattr(obj, key, convert_nested_object(value))
                        return obj
                    elif isinstance(data, list):
                        return [convert_nested_object(item) for item in data]
                    else:
                        return data

                fields = type('Fields', (), {})()
                for key, value in fields_data.items():
                    setattr(fields, key, convert_nested_object(value))

                issue = type('Issue', (), {
                    'key': issue_data['key'],
                    'fields': fields
                })()

                ticket_info = self._format_ticket_info(issue)
                all_tickets.append(ticket_info)
                subtask_count += len(ticket_info.get('subtasks', []))

            print(f"子チケット: {subtask_count}件")
            print(f"合計: {len(all_tickets)}件（親チケット）+ {subtask_count}件（子チケット）")

            return all_tickets
        except Exception as e:
            print(f"v3検索エラー: {e}")
            return []

    def search_tickets(self, jql_query, max_results=50):
        try:
            print(f"JQLクエリ実行中: {jql_query}")
            # まずv3 APIを試す
            return self.search_tickets_v3(jql_query, max_results)
        except Exception as e:
            print(f"v3 API失敗、従来方法で再試行: {e}")
            try:
                # 従来の方法でフォールバック
                issues = self.jira.search_issues(jql_query, maxResults=max_results)
                print(f"検索結果: {len(issues)}件のチケットが見つかりました")

                all_tickets = []
                subtask_count = 0

                for issue in issues:
                    ticket_info = self._format_ticket_info(issue)
                    all_tickets.append(ticket_info)
                    subtask_count += len(ticket_info.get('subtasks', []))

                print(f"子チケット: {subtask_count}件")
                print(f"合計: {len(all_tickets)}件（親チケット）+ {subtask_count}件（子チケット）")

                return all_tickets
            except Exception as fallback_e:
                print(f"チケット検索エラー: {fallback_e}")
                print(f"エラータイプ: {type(fallback_e).__name__}")
                print(f"JQLクエリ: {jql_query}")
                if hasattr(fallback_e, 'status_code'):
                    print(f"HTTPステータスコード: {fallback_e.status_code}")
                if hasattr(fallback_e, 'response'):
                    print(f"レスポンス内容: {fallback_e.response.text if hasattr(fallback_e.response, 'text') else fallback_e.response}")
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

    def get_subtasks(self, issue_key):
        try:
            issue = self.jira.issue(issue_key)
            if hasattr(issue.fields, 'subtasks') and issue.fields.subtasks:
                subtasks = []
                for subtask in issue.fields.subtasks:
                    subtask_issue = self.jira.issue(subtask.key)
                    subtasks.append(self._format_ticket_info(subtask_issue, include_subtasks=False))
                return subtasks
            return []
        except Exception as e:
            print(f"子チケット取得エラー: {e}")
            return []

    def _format_ticket_info(self, issue, include_subtasks=True):
        def safe_get(obj, attr, default=None):
            try:
                value = getattr(obj, attr, default)
                if value is None:
                    return default
                # PropertyHolderオブジェクトの場合は、より詳細な情報を取得
                if hasattr(value, '__dict__') and 'PropertyHolder' in str(type(value)):
                    return None  # PropertyHolderは無視
                # 辞書の場合はそのまま値を取得
                if isinstance(value, dict):
                    return str(value)
                return str(value)
            except Exception:
                return default


        ticket_info = {
            'key': str(issue.key) if issue.key else None,
            'summary': str(issue.fields.summary) if issue.fields.summary else None,
            'description': safe_get(issue.fields, 'description'),
            'status': safe_get(issue.fields.status, 'name') if hasattr(issue.fields, 'status') and issue.fields.status else None,
            'assignee': safe_get(issue.fields.assignee, 'displayName') if issue.fields.assignee else None,
            'reporter': safe_get(issue.fields.reporter, 'displayName') if issue.fields.reporter else None,
            'created': str(issue.fields.created) if issue.fields.created else None,
            'updated': str(issue.fields.updated) if issue.fields.updated else None,
            'priority': safe_get(issue.fields.priority, 'name') if issue.fields.priority else None,
            'issue_type': safe_get(issue.fields.issuetype, 'name'),
            'project': safe_get(issue.fields.project, 'key'),
            'parent': safe_get(issue.fields.parent, 'key') if hasattr(issue.fields, 'parent') and issue.fields.parent else None
        }

        if include_subtasks:
            subtasks = self.get_subtasks(issue.key)
            ticket_info['subtasks'] = subtasks
            ticket_info['subtask_count'] = len(subtasks)

        return ticket_info

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
                if ticket.get('subtasks'):
                    for subtask in ticket['subtasks']:
                        print(f"  └─ {subtask['key']}: {subtask['summary']} [{subtask['status']}]")

            # JSONファイルにエクスポート
            manager.export_to_json(tickets, f"{project_key}_tickets.json")

if __name__ == "__main__":
    main()