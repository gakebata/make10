# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

入力した数字を四則演算 (`+ - * /` と括弧) で組み合わせ、目標値 (既定 10) になる式を列挙するパズルソルバー。

## コマンド

開発環境のセットアップと主要コマンド (Python >= 3.10):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"        # pytest, ruff 込みの開発インストール

pytest                          # 全テスト
pytest tests/test_core.py::test_canonical_associative_equal   # 単一テスト
ruff check .                    # lint
make10 1234                     # CLI 実行 (エントリポイントは make10.cli:main)
```

`pyproject.toml` の `[tool.pytest.ini_options]` で `pythonpath = ["src"]` を設定済みのため、
`pytest` は追加の環境変数なしで `src/` レイアウトを解決する。

## アーキテクチャ

すべてのソルバーロジックは [src/make10/core.py](src/make10/core.py) に集約されており、
[src/make10/cli.py](src/make10/cli.py) はその薄いラッパー。設計の要点:

- **式は文字列ではなく木 (`Num` / `BinOp`) として表現する。** 旧実装の `eval` は
  意図的に排除している。新しい計算ロジックを足すときも文字列を `eval` せず、
  木を組み立てて `evaluate()` を通すこと。
- **計算はすべて `fractions.Fraction`。** 浮動小数点を経由すると `8 / (3 - 8 / 3)` のような
  解が `23.999...` となり目標値判定で取りこぼす。float を導入しないこと。
- **解の生成は `_generate()` の再帰** で、葉ノード列から「2 つ選んで演算子で結合し残りと再帰」
  を繰り返し、全ての順序・グループ化・演算子を網羅する。桁数固定のハードコードは無い。
- **重複除去は 2 段構え** ([find_solutions](src/make10/core.py) 内): `canonical()` が可換 (`+`,`*`) の
  項ソートと結合則の平坦化で等価式を同一視し、加えて `render()` の出力文字列でも照合する。
  既知の制約として、加減の順序違い (`2*4+3-1` と `2*4-1+3`) は等価でも別表示として残る。
- **`render()` は優先順位に基づき括弧を最小化する。** 同順位の右側かつ親が `-`/`/` のときのみ括弧を付ける。

入力解釈 (`parse_tokens`): 区切り無しの文字列は 1 文字ずつ (`"1234"` → 1,2,3,4)、
空白/カンマ区切りは複数桁 (`"12 3 4"` → 12,3,4) として扱う。

## 旧実装

歴史的経緯の保存として、初期の実装を 2 つそのまま残している (いずれも改修しない):

- [make10_origin.py](make10_origin.py) — 最初期版。括弧が無く桁数ごとにループを手書きした原型。
- [make10_legacy.py](make10_legacy.py) — その次の版。括弧パターンを加えた、現行ソルバーの直接の前身。

どちらも `eval`・桁数ハードコード・浮動小数点を含むため **ruff の対象外**
(`pyproject.toml` の `extend-exclude`) としている。
