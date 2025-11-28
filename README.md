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

### ツール

- **get_weather_stateful**: セッション状態から温度単位設定を読み取り、指定された都市の天気情報を返す
- **get_current_time**: 指定された都市の現在時刻を返す
- **say_hello**: 挨拶メッセージを生成（オプションで名前を指定可能）
- **say_goodbye**: 別れのメッセージを生成

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
│   └── farewell_agent/        # 別れ専門エージェント
│       ├── agent.py
│       ├── tools/
│       │   └── say_goodbye.py
│       └── __init__.py
├── guardrail/
│   ├── block_keyword_guardrail.py
│   └── block_paris_tool_guardrail.py
├── main.py                    # メインエントリーポイント
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

## 使用方法

### アプリケーションの実行

```bash
uv run main.py
```

### adk webの起動

```bash
uv run adk web agents
```
