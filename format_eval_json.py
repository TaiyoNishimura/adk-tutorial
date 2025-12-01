"""
Evaluation JSONファイルを整形するスクリプト

使い方:
  uv run format_eval_json.py <agent_name>

引数:
  agent_name : エージェント名（例: bigquery）
"""

import json
import sys
from pathlib import Path


def format_json_file(agent_name: str):
    """
    エージェントの評価結果JSONファイルを全て読み込んで整形する

    Args:
        agent_name: エージェント名
    """
    # 評価結果ディレクトリ
    eval_history_dir = Path(f"agents/{agent_name}/.adk/eval_history")

    if not eval_history_dir.exists():
        print(f"エラー: ディレクトリが見つかりません: {eval_history_dir}")
        sys.exit(1)

    # 全ての評価結果ファイルを検索（フォーマット済みを除く）
    eval_files = [
        f for f in eval_history_dir.glob("*.evalset_result.json")
        if "_formatted" not in f.stem
    ]

    if not eval_files:
        print(f"エラー: 評価結果ファイルが見つかりません: {eval_history_dir}/*.evalset_result.json")
        sys.exit(1)

    print(f"{len(eval_files)}個のファイルを処理します\n")

    success_count = 0
    error_count = 0

    for input_file in eval_files:
        output_file = input_file.parent / f"{input_file.stem}_formatted.json"

        print(f"処理中: {input_file.name}")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            try:
                data = json.loads(content)
                if isinstance(data, str):
                    data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"  ✗ JSONのパースに失敗: {e}\n")
                error_count += 1
                continue

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"  ✓ 完了: {output_file.name}\n")
            success_count += 1

        except Exception as e:
            print(f"  ✗ エラー: {e}\n")
            error_count += 1

    print(f"{'='*50}")
    print(f"処理完了: 成功 {success_count}件, 失敗 {error_count}件")


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n例:")
        print("  uv run format_eval_json.py bigquery")
        sys.exit(1)

    agent_name = sys.argv[1]
    format_json_file(agent_name)


if __name__ == "__main__":
    main()
