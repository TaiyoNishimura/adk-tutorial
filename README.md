# ADKチュートリアル - マルチエージェント天気アプリケーション

Google ADK (Agent Development Kit) を使用したマルチエージェントシステムのチュートリアルプロジェクトです。エージェント間の委譲、ステートフルな会話、ガードレールの実装など、ADKの主要な機能を実演します。

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

### 実行例

main.pyには以下のようなステートフルな会話のデモが含まれています：

1. **ロンドンの天気を確認**（摂氏で表示）
2. **温度単位を華氏に変更**（セッション状態を手動で更新）
3. **ニューヨークの天気を確認**（華氏で表示）
4. **挨拶を送信**（greeting_agentに委譲）

### カスタマイズ

- **新しいツールの追加**: `agents/[agent_name]/tools/` ディレクトリに新しいツールを追加
- **新しいエージェントの追加**: `agents/` ディレクトリに新しいエージェントディレクトリを作成
- **ガードレールの追加**: `guardrail/` ディレクトリに新しいガードレールを追加
- **温度単位の変更**: セッション状態の `user_preference_temperature_unit` を "Celsius" または "Fahrenheit" に設定

## 主要概念

### エージェント委譲

メインエージェント（weather_agent_v1）は、挨拶や別れの挨拶を専門エージェントに委譲します。これにより、各エージェントが特定のタスクに集中できます。

### セッション管理

InMemorySessionServiceを使用して、ユーザーごとのセッション状態を管理します。本番環境では、Database SessionServiceやVertexAI SessionServiceを使用できます。

### ガードレール

- **before_model_callback**: LLMモデル呼び出し前に実行され、リクエストをブロックまたは変更できます
- **before_tool_callback**: ツール実行前に実行され、特定のツール呼び出しをブロックできます

### output_key

エージェントの最終応答をセッション状態に自動的に保存するためのキー。`output_key="last_weather_report"` により、天気レポートが状態に保存されます。

## 依存関係

- `google-adk>=1.18.0`: Google Agent Development Kit
- `python-dotenv>=1.2.1`: 環境変数管理

## ライセンス

このプロジェクトはチュートリアル目的で作成されています。

## 参考資料

- [Google ADK ドキュメント](https://cloud.google.com/agent-development-kit)
- [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs)
