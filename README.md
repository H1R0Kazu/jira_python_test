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
4. **子チケット自動収集**: 親チケットの子チケットも自動取得・階層表示
5. **フィルタ機能**:
   - プロジェクト別
   - 担当者別
   - ステータス別
6. **データエクスポート**: 取得したデータをJSONファイルに保存
7. **API v3対応**: 最新のJira REST API v3に完全対応

## 開発中に発見された問題と対応

### 1. Jira API v2 廃止エラー (HTTP 410)

**問題**:
```
JiraError HTTP 410: リクエストされた API は廃止されています。
/rest/api/3/search/jql の API に移行してください。
```

**原因**: Jira API v2が廃止され、v3への移行が必要

**対応**:
- `jira_config.py`: `rest_api_version: '3'`を明示的に設定
- `jira_ticket_manager.py`:
  - `search_tickets_v3()`関数で直接v3エンドポイントを使用
  - フォールバック機能により従来ライブラリも併用可能
  - `requests`ライブラリで直接`/rest/api/3/search/jql`を呼び出し

### 2. JSON シリアライゼーションエラー

**問題**:
```
TypeError: Object of type PropertyHolder is not JSON serializable
```

**原因**: JiraライブラリのPropertyHolderオブジェクトがJSON出力時にエラー

**対応**:
- `_format_ticket_info()`に`safe_get()`ヘルパー関数を実装
- PropertyHolderオブジェクトを検出してnullに変換
- 全フィールドの安全な文字列変換処理

### 3. 子チケット取得の実装

**問題**: 検索結果に子チケットが含まれない

**対応**:
- `get_subtasks()`関数で親チケットの子チケットを自動取得
- `include_subtasks=False`による無限再帰防止
- 階層表示機能（`└─`マーク）の実装
- v3 APIデータ構造に対応したオブジェクト変換

### 4. v3 APIデータ構造の違い

**問題**: v3 APIのデータ構造がライブラリの期待と異なる

**対応**:
- `convert_nested_object()`関数でJSON→オブジェクト変換
- ネストしたオブジェクト（status, assignee等）の適切な処理
- デバッグ出力機能の追加

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

### API 410エラーが発生する場合
1. ライブラリのバージョンを確認
2. v3エンドポイントが正しく使用されているか確認
3. `search_tickets_v3()`関数が正常に動作するか確認

### JSONエクスポートでエラーが発生する場合
1. PropertyHolderオブジェクトの存在を確認
2. `safe_get()`関数が適切に動作しているか確認
3. デバッグ出力を有効化して問題を特定

## 技術メモ

- **API互換性**: Jira API v2は2025年以降廃止予定のため、v3への移行必須
- **データ変換**: PropertyHolderオブジェクトはJiraライブラリの内部実装詳細
- **パフォーマンス**: 子チケットの取得にはAPIコール数の制限に注意
- **データ構造**: v3 APIのデータ構造は v2 と異なるため、適切な変換が必要

## 今後の改善点

- [ ] ステータス表示の修正（現在一部で`[None]`となる問題）
- [ ] より詳細なエラーハンドリング
- [ ] バルク処理の最適化
- [ ] フィルタリング機能の追加
- [ ] CSV/Excel出力対応
- [ ] キャッシュ機能の実装