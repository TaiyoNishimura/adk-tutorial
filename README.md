# ADKチュートリアル - マルチエージェント天気アプリケーション

個人開発で使用しているGoogle ADK (Agent Development Kit) を使用したマルチエージェントシステムのチュートリアルプロジェクトです。

[公式のリポジトリ](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)を参照ください。

## プロジェクト概要

このアプリケーションは、天気情報を提供するメインエージェントと、挨拶・別れの挨拶を担当する専門エージェントから構成されています。セッション状態を管理し、ユーザーの設定（温度単位など）を記憶します。

## 機能

### エージェント

- **weather_agent_v1** (メインエージェント)
  - 天気情報のクエリを処理
  - 挨拶と別れのメッセージを専門エージェントに委譲
  - セッション状態を管理
  - ツール実行前のガードレールを適用

- **greeting_agent** (挨拶エージェント)
  - ユーザーの挨拶に応答
  - LLMモデル呼び出し前のガードレールを適用

- **farewell_agent** (別れエージェント)
  - ユーザーの別れの挨拶に応答

- **bigquery_agent** (BigQueryエージェント)
  - 自然言語からBigQuery SQLを生成・実行
  - NL2SQLツールを使用してSQLクエリを生成
  - BigQueryのexecute_sqlツール（ADK組み込み）でクエリを実行
  - 日本語での質問と回答に対応
  - JSON形式で詳細な結果を返却（説明、SQL、実行結果、自然言語サマリー）

### ガードレール

- **block_keyword_guardrail**: 特定のキーワード（"BLOCK"）を含むリクエストをブロック（LLMモデル呼び出し前）
- **block_paris_tool_guardrail**: パリの天気情報取得をブロック（ツール実行前）

### ステート管理

- ユーザーの温度単位設定（摂氏/華氏）
- 最後に確認した都市
- 最後の天気レポート
- ガードレールトリガーのフラグ

## プロジェクト構造

```
adk-tutorial/
├── agents/
│   ├── my_agent/              # メイン天気エージェント
│   │   ├── agent.py
│   │   ├── tools/
│   │   │   ├── get_weather.py
│   │   │   └── get_current_time.py
│   │   └── __init__.py
│   ├── greeting_agent/        # 挨拶専門エージェント
│   │   ├── agent.py
│   │   ├── tools/
│   │   │   └── say_hello.py
│   │   └── __init__.py
│   ├── farewell_agent/        # 別れ専門エージェント
│   │   ├── agent.py
│   │   ├── tools/
│   │   │   └── say_goodbye.py
│   │   └── __init__.py
│   └── bigquery/              # BigQuery NL2SQLエージェント
│       ├── agent.py
│       ├── config/
│       │   ├── bigquery_data_config.py
│       │   └── nl2sql_model.py
│       ├── tools/
│       │   └── nl2sql.py
│       ├── data/
│       │   └── products.csv
│       ├── .env.example
│       └── __init__.py
├── guardrail/
│   ├── block_keyword_guardrail.py
│   └── block_paris_tool_guardrail.py
├── docs/                      # ドキュメント
│   ├── trouble_shooting_adk_web_module_not_found_error.md
│   └── trouble_shooting_eval_not_found.md
├── main.py                    # メインエントリーポイント
├── format_eval_json.py        # 評価結果フォーマットツール
├── pyproject.toml
└── README.md
```

## セットアップ

### 必要要件

- Python 3.13+
- UV（推奨）またはpip

### インストール

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd adk-tutorial
```

2. 環境変数の設定:
```bash
# agents/my_agent/.env ファイルを作成し、必要なAPIキーを設定
```

3. 依存関係のインストール:
```bash
uv sync
```

### Docker Composeでデータベースを起動

Dev Containerを使用している場合、PostgreSQLとpgAdminは自動的に起動しています。

手動で起動する場合：
```bash
cd .devcontainer
docker compose up -d
```

起動したサービス：
- **PostgreSQL**: localhost:5432
  - ユーザー名: `user`
  - パスワード: `password`
  - データベース名: `db`
- **pgAdmin**: http://localhost:8080
  - メールアドレス: `admin@admin.com`
  - パスワード: `admin`

### pgAdminでデータベースを確認

1. ブラウザで http://localhost:8080 を開く
2. メールアドレス（`admin@admin.com`）とパスワード（`admin`）でログイン
3. 左メニューの「Add New Server」をクリック
4. 接続情報を入力：
   - **General > Name**: 任意の名前（例：`ADK Database`）
   - **Connection > Host**: `localhost`
   - **Connection > Port**: `5432`
   - **Connection > Username**: `user`
   - **Connection > Password**: `password`
5. 「Save」をクリックして接続

## 使用方法

### アプリケーションの実行

```bash
uv run main.py
```

### adk webの起動

```bash
uv run adk web agents
```

### 評価結果のフォーマット

評価結果のJSONファイルを読みやすい形式に整形します：

```bash
uv run format_eval_json.py <agent_name>
```

例：
```bash
uv run format_eval_json.py bigquery
```