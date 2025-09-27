# Jira Python API テスト

PythonでAtlassian JiraのAPIにアクセスしてチケット情報を取得するサンプルプロジェクトです。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、以下の情報を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

### 3. Jira APIトークンの取得方法

1. Atlassianアカウントにログイン
2. [API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)ページにアクセス
3. 「Create API token」をクリック
4. トークン名を入力して作成
5. 生成されたトークンをコピーして`.env`ファイルに設定

## 使用方法

### 基本的な使用例

```python
from jira_ticket_manager import JiraTicketManager

# インスタンス作成
manager = JiraTicketManager()

# 特定のチケットを取得
ticket = manager.get_ticket("PROJECT-123")
print(ticket)

# プロジェクトのチケット一覧を取得
tickets = manager.get_tickets_by_project("PROJECT", 20)

# 担当者でフィルタ
my_tickets = manager.get_tickets_by_assignee("user@example.com")

# ステータスでフィルタ
open_tickets = manager.get_tickets_by_status("Open")
```

### インタラクティブな実行

```bash
python jira_ticket_manager.py
```

このコマンドで対話形式でチケット情報を取得できます。

## ファイル構成

- `jira_config.py`: Jira接続設定とクライアント作成
- `jira_ticket_manager.py`: チケット取得・管理のメインクラス
- `requirements.txt`: 必要なPythonパッケージ
- `.env.example`: 環境変数のテンプレート

## 主な機能

1. **接続テスト**: Jiraサーバーへの接続確認
2. **チケット取得**: 特定のチケットキーで詳細情報を取得
3. **チケット検索**: JQLクエリを使用した柔軟な検索
4. **フィルタ機能**:
   - プロジェクト別
   - 担当者別
   - ステータス別
5. **データエクスポート**: 取得したデータをJSONファイルに保存

## トラブルシューティング

### 認証エラー
- APIトークンが正しく設定されているか確認
- Jira URLが正しいか確認（https://を含む）
- ユーザー名（メールアドレス）が正しいか確認

### 権限エラー
- Jiraプロジェクトへのアクセス権限があるか確認
- APIトークンに必要な権限が付与されているか確認

### 接続エラー
- ネットワーク接続を確認
- ファイアウォールの設定を確認
- JiraサーバーのURLが正しいか確認