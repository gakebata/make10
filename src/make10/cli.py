"""make10 のコマンドラインインターフェース.

使い方::

    make10 1234              # 1,2,3,4 で 10 を作る式を表示
    make10 --target 24 1234  # 目標値を 24 に
    make10 "12 3 4"          # 空白区切りで複数桁の数値
    make10                   # 引数なしなら対話モード
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from make10.core import find_solutions


def _print_solutions(text: str, target: int, *, dedup: bool) -> None:
    solutions = find_solutions(text, target, dedup=dedup)
    for formula in solutions:
        print(f"{formula} = {target}")
    print(f"[Count: {len(solutions)}]")


def _interactive(target: int, *, dedup: bool) -> None:
    print("数字を入力すると四則演算して目標値になる式を列挙します ('end' で終了)")
    while True:
        try:
            text = input("number? = ")
        except EOFError:
            break
        if text == "end":
            break
        _print_solutions(text, target, dedup=dedup)
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="make10",
        description="入力した数字を四則演算して目標値 (既定 10) を作る式を列挙する。",
    )
    parser.add_argument(
        "numbers",
        nargs="?",
        help='数字 (例 "1234" または空白/カンマ区切り "12 3 4")。省略すると対話モード。',
    )
    parser.add_argument(
        "-t",
        "--target",
        type=int,
        default=10,
        help="目標値 (既定: 10)",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="重複する式を除去せずすべて表示する",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    dedup = not args.no_dedup
    if args.numbers is None:
        _interactive(args.target, dedup=dedup)
    else:
        _print_solutions(args.numbers, args.target, dedup=dedup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
