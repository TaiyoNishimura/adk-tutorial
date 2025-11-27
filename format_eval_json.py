"""
Evaluation JSONファイルを整形するスクリプト

使い方:
  uv run format_eval_json.py <input_file> [output_file]

引数:
  input_file  : 整形したいJSONファイルのパス
  output_file : 出力先（省略可。デフォルトは元のファイル名に _formatted を付加）
"""

import json
import sys
from pathlib import Path


def format_json_file(input_path: str, output_path: str = None):
    """
    JSONファイルを読み込んで整形する

    Args:
        input_path: 入力ファイルのパス
        output_path: 出力ファイルのパス（Noneの場合は自動生成）
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)

    # 出力ファイル名を決定
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}_formatted{input_file.suffix}"
    else:
        output_file = Path(output_path)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        try:
            data = json.loads(content)
            if isinstance(data, str):
                data = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"エラー: JSONのパースに失敗しました: {e}")
            sys.exit(1)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("✓ 整形完了！")

    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n例:")
        print("  uv run format_eval_json.py agents/my_agent/.adk/eval_history/result.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    format_json_file(input_file, output_file)


if __name__ == "__main__":
    main()
