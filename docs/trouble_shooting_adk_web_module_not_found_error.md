# adk webを実行した時に発生したModuleNotFoundErrorを解決する

## 1. 最初に発生したエラー

### エラーメッセージ

```python
ModuleNotFoundError: No module named 'guardrail'
```

### 発生箇所

`agents/my_agent/agent.py`の3行目：

```python
from guardrail import block_paris_tool_guardrail
```

### 状況

実際にはプロジェクトのルートディレクトリに`guardrail/`フォルダが存在している：

```
adk-tutorial/
├── guardrail/
│   ├── __init__.py
│   ├── block_paris_tool_guardrail.py
│   └── block_keyword_guardrail.py
└── agents/
    └── my_agent/
        └── agent.py
```

**疑問：ファイルは存在しているのに、なぜPythonは「見つからない」と言っているのか？**

## 2. ADK Web Serverがエージェントを読み込む仕組み

### 基本動作

`adk web agents`を実行すると、ADKは`agents/`ディレクトリ内の各サブディレクトリを個別のエージェントモジュールとして読み込みます。

### 通常の可視範囲

`agents/`の中から見える範囲は基本的に：
- 同じディレクトリ内のモジュール（`.tools`など相対インポート）
- 標準ライブラリ
- インストール済みのパッケージ

プロジェクトルートの`guardrail/`は**同じディレクトリではない**ので通常は見えません。

### エディタブルインストールによる解決

`pyproject.toml`でプロジェクト全体をパッケージとして定義し、**エディタブルインストール**を実行することで、この問題を解決しています。

## 3. エディタブルインストールの設定方法

pyproject.tomlに追加

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["agents*", "guardrail*"]
```

パッケージをインストール
```bash
uv sync
```

### 作成されるファイル

`.venv/lib/python3.13/site-packages/`に以下のファイルが作成されます：

1. **`__editable___adk_tutorial_0_1_0_finder.py`**
   - カスタムインポート検索機

2. **`__editable__.adk_tutorial-0.1.0.pth`**
   - Python起動時に実行される設定ファイル

### MAPPINGによるパス解決

`__editable___adk_tutorial_0_1_0_finder.py`の中身：

```python
MAPPING: dict[str, str] = {
    'agents': '/workspaces/adk-tutorial/agents',
    'guardrail': '/workspaces/adk-tutorial/guardrail'
}
```

**動作の流れ：**

1. Pythonが`import guardrail`を実行しようとする
2. カスタムファインダーが`sys.meta_path`に登録されている
3. ファインダーが「`guardrail`は`/workspaces/adk-tutorial/guardrail`にある」と教える
4. その場所からモジュールを読み込む

### エディタブルインストールの利点

**通常のインストール：**
- ファイルが`.venv`にコピーされる
- コードを編集したら再インストールが必要

**エディタブルインストール：**
- ファイルをコピーせず、**元の場所を直接参照**
- コードを編集したら即座に反映される（再インストール不要）
- 開発中のパッケージに最適

## 4. それなのになぜエラーが発生したのか？

### エラートレースバックの分析

```
File "/home/vscode/.local/share/uv/tools/google-adk/lib/python3.12/site-packages/google/adk/cli/adk_web_server.py"
```

**重要なポイント：**
- パスが `/home/vscode/.local/share/uv/tools/google-adk/` を指している
- `python3.12` と書かれている

プロジェクトの環境とは異なる！
- プロジェクト: `.venv/lib/python3.13/site-packages/`
- Python: 3.13

### 2つのADKが存在

システムには2つの異なるADK環境がインストールされていました：

#### 環境1: UV tools版のADK

```
場所: /home/vscode/.local/share/uv/tools/google-adk/
Python: 3.12
バージョン: 1.19.0
エディタブルインストール: なし
結果: guardrailモジュールが見えない ✗
```

#### 環境2: プロジェクト.venv版のADK

```
場所: /workspaces/adk-tutorial/.venv/
Python: 3.13
バージョン: 1.18.0
エディタブルインストール: あり
結果: guardrailモジュールが見える ✓
```

### 問題の核心

単に`adk web agents`と実行した場合：
- シェルのPATHから最初に見つかった`adk`コマンドが実行される
- **UV tools版のADK（環境1）が使われていた**
- エディタブルインストールの恩恵を受けられない
- `guardrail`モジュールが見つからない

## 5. なぜ `uv run adk web agents` で動作したのか？

### `uv run` コマンドの特別な動作

`uv run`は単にコマンドを実行するだけでなく、**プロジェクトのコンテキストで実行**します。

#### 具体的な動作

1. **プロジェクトの `.venv` を自動的に認識**
   - `pyproject.toml` があるディレクトリで実行すると
   - そのプロジェクトの仮想環境を使用する

2. **正しいPython環境でコマンドを実行**
   - `.venv/bin/python` を使用
   - `.venv` にインストールされたパッケージが利用可能
   - エディタブルインストールも有効

### 実行の違い

#### `adk web agents` の場合

```bash
# シェルのPATHから最初に見つかった "adk" を実行
# ↓
# UV tools版のadk（Python 3.12環境）が実行された
# ↓
# guardrailモジュールが見つからない ✗
```

#### `uv run adk web agents` の場合

```bash
# uvが .venv/bin/adk を明示的に実行
# ↓
# プロジェクトのPython 3.13環境で実行
# ↓
# エディタブルインストールが有効
# ↓
# guardrailモジュールが見つかる ✓
```

## まとめ

### 問題の本質

1. プロジェクトはエディタブルインストールで正しく設定されていた
2. しかし、間違ったPython環境（UV tools版）でADKが実行されていた
3. その環境にはエディタブルインストールの設定がなかった

### 解決策

`uv run`を使用することで：
- プロジェクトの仮想環境が自動的に使用される
- エディタブルインストールが有効になる
- `guardrail`モジュールが正しくインポートできる
