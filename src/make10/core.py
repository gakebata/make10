"""make10 のコアエンジン.

数式を文字列として組み立てて ``eval`` する旧実装を廃し、

* 式を木構造 (:class:`Num` / :class:`BinOp`) として表現
* :class:`fractions.Fraction` による厳密計算 (浮動小数点誤差なし)
* 任意個数の数値・全グループ化を再帰で網羅
* 可換・結合則を考慮した正規化による重複除去

を行う。
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from fractions import Fraction

# 演算子と、その二項演算の実装
OPS: dict[str, Callable[[Fraction, Fraction], Fraction]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}

# 演算子の優先順位 (括弧の最小化に使用)
_PRECEDENCE: dict[str, int] = {"+": 1, "-": 1, "*": 2, "/": 2}


@dataclass(frozen=True)
class Num:
    """葉ノード: 1 つの数値."""

    value: Fraction
    text: str  # 表示用の元トークン (例: "12")


@dataclass(frozen=True)
class BinOp:
    """二項演算ノード."""

    op: str
    left: Expr
    right: Expr


Expr = Num | BinOp


# -------------------- 入力の解釈 --------------------
def parse_tokens(text: str) -> list[Num]:
    """入力文字列を数値の葉ノード列に変換する.

    空白かカンマ区切りがあれば複数桁の数値として分割し
    (例 ``"12 3 4"`` -> 12, 3, 4)、区切りが無ければ
    旧実装と同様に 1 文字ずつに分解する (例 ``"1234"`` -> 1,2,3,4)。
    """
    text = text.strip()
    if not text:
        return []
    if re.search(r"[,\s]", text):
        parts = [p for p in re.split(r"[,\s]+", text) if p]
    else:
        parts = list(text)
    return [Num(Fraction(p), p) for p in parts]


# -------------------- 評価 --------------------
def evaluate(expr: Expr) -> Fraction:
    """式木を厳密に評価する. ゼロ除算は :class:`ZeroDivisionError`."""
    if isinstance(expr, Num):
        return expr.value
    return OPS[expr.op](evaluate(expr.left), evaluate(expr.right))


# -------------------- 文字列化 (括弧最小化) --------------------
def render(expr: Expr) -> str:
    """演算子の優先順位に従い、必要最小限の括弧で文字列化する."""
    if isinstance(expr, Num):
        return expr.text
    prec = _PRECEDENCE[expr.op]
    left = _render_child(expr.left, prec, is_right=False, parent_op=expr.op)
    right = _render_child(expr.right, prec, is_right=True, parent_op=expr.op)
    return f"{left} {expr.op} {right}"


def _render_child(child: Expr, parent_prec: int, *, is_right: bool, parent_op: str) -> str:
    s = render(child)
    if isinstance(child, Num):
        return s
    child_prec = _PRECEDENCE[child.op]
    # 優先順位が低ければ必ず括弧
    need = child_prec < parent_prec
    # 同順位でも、右側 かつ 親が左結合で意味が変わる演算 (- /) なら括弧
    if child_prec == parent_prec and is_right and parent_op in ("-", "/"):
        need = True
    return f"({s})" if need else s


# -------------------- 正規化 (重複除去用) --------------------
CanonKey = tuple


def canonical(expr: Expr) -> CanonKey:
    """数学的に等価な式が同じキーになる正規形を返す.

    可換 (+, *) は項をソートし、結合則も平坦化して吸収する。
    これにより ``1 + 2`` と ``2 + 1``、``(1 + 2) + 3`` と
    ``1 + (2 + 3)`` などが同一視される。
    """
    if isinstance(expr, Num):
        return ("n", expr.value)
    op = expr.op
    if op in ("+", "*"):
        terms = sorted(canonical(t) for t in _flatten(expr, op))
        return (op, tuple(terms))
    return (op, canonical(expr.left), canonical(expr.right))


def _flatten(expr: Expr, op: str) -> list[Expr]:
    if isinstance(expr, BinOp) and expr.op == op:
        return _flatten(expr.left, op) + _flatten(expr.right, op)
    return [expr]


# -------------------- 式の生成 --------------------
def _generate(exprs: list[Expr]) -> Iterator[Expr]:
    """葉ノード列から、全ての順序・グループ化・演算子の式木を生成する."""
    if len(exprs) == 1:
        yield exprs[0]
        return
    n = len(exprs)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            rest = [exprs[k] for k in range(n) if k != i and k != j]
            for op in OPS:
                yield from _generate(rest + [BinOp(op, exprs[i], exprs[j])])


# -------------------- 公開 API --------------------
def find_solutions(
    text: str, target: int | Fraction = 10, *, dedup: bool = True
) -> list[str]:
    """``text`` の数値を四則演算して ``target`` になる式の一覧を返す."""
    leaves: list[Expr] = list(parse_tokens(text))
    if not leaves:
        return []
    target = Fraction(target)
    results: list[str] = []
    seen_keys: set[CanonKey] = set()
    seen_text: set[str] = set()
    for expr in _generate(leaves):
        try:
            value = evaluate(expr)
        except ZeroDivisionError:
            continue
        if value != target:
            continue
        text_repr = render(expr)
        if dedup:
            # 正規形 (可換・結合則を吸収) と文字列の両方で重複を除く。
            # 正規形は 1+2 と 2+1 を、文字列は a+b-c と a+(b-c) のように
            # 木は異なるが見た目が同じ式を取り除く。
            key = canonical(expr)
            if key in seen_keys or text_repr in seen_text:
                continue
            seen_keys.add(key)
            seen_text.add(text_repr)
        results.append(text_repr)
    return results
