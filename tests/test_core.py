"""コアエンジンのテスト."""

from __future__ import annotations

import re
from fractions import Fraction

import pytest

from make10.core import (
    BinOp,
    Num,
    canonical,
    evaluate,
    find_solutions,
    parse_tokens,
    render,
)


def n(value: int) -> Num:
    """テスト用の数値ノードを簡潔に作るヘルパ."""
    return Num(Fraction(value), str(value))


# -------------------- parse_tokens --------------------
def test_parse_single_string_splits_per_char():
    tokens = parse_tokens("1234")
    assert [t.text for t in tokens] == ["1", "2", "3", "4"]
    assert [t.value for t in tokens] == [Fraction(n) for n in (1, 2, 3, 4)]


def test_parse_space_separated_multi_digit():
    tokens = parse_tokens("12 3 4")
    assert [t.value for t in tokens] == [Fraction(12), Fraction(3), Fraction(4)]


def test_parse_comma_separated():
    tokens = parse_tokens("12,34")
    assert [t.value for t in tokens] == [Fraction(12), Fraction(34)]


def test_parse_empty():
    assert parse_tokens("   ") == []


# -------------------- evaluate --------------------
def test_evaluate_is_exact():
    # (1 + 2 - 3) / 4 == 0、誤差なし
    expr = BinOp("/", BinOp("-", BinOp("+", n(1), n(2)), n(3)), n(4))
    assert evaluate(expr) == Fraction(0)


def test_evaluate_division_raises_on_zero():
    expr = BinOp("/", n(1), n(0))
    with pytest.raises(ZeroDivisionError):
        evaluate(expr)


# -------------------- render (括弧最小化) --------------------
def test_render_minimizes_parentheses():
    # (1 + 2) * 3 は左の括弧が必須
    expr = BinOp("*", BinOp("+", n(1), n(2)), n(3))
    assert render(expr) == "(1 + 2) * 3"


def test_render_no_parens_when_unneeded():
    # 1 + 2 * 3 は括弧不要
    expr = BinOp("+", n(1), BinOp("*", n(2), n(3)))
    assert render(expr) == "1 + 2 * 3"


def test_render_right_subtraction_needs_parens():
    # 1 - (2 - 3) は右の括弧が必須
    expr = BinOp("-", n(1), BinOp("-", n(2), n(3)))
    assert render(expr) == "1 - (2 - 3)"


# -------------------- canonical (重複除去) --------------------
def test_canonical_commutative_equal():
    a = BinOp("+", n(1), n(2))
    b = BinOp("+", n(2), n(1))
    assert canonical(a) == canonical(b)


def test_canonical_associative_equal():
    # (1 + 2) + 3 と 1 + (2 + 3)
    a = BinOp("+", BinOp("+", n(1), n(2)), n(3))
    b = BinOp("+", n(1), BinOp("+", n(2), n(3)))
    assert canonical(a) == canonical(b)


def test_canonical_subtraction_order_matters():
    a = BinOp("-", n(1), n(2))
    b = BinOp("-", n(2), n(1))
    assert canonical(a) != canonical(b)


# -------------------- find_solutions --------------------
def test_results_are_all_correct_and_unique():
    results = find_solutions("1234", 10)
    assert results
    assert len(results) == len(set(results))  # 重複なし
    # 表示された各式が実際に 10 になることを (厳密に) 確認
    for formula in results:
        assert evaluate_str(formula) == 10


def test_known_classic_solution_present():
    # (1 + 2 + 3) * 4 ではなく、有名な 1 2 3 4 -> 10 の解の一例
    results = find_solutions("1234", 10)
    assert "1 + 2 + 3 + 4" in results


def test_no_float_error_division_case():
    # 3 3 8 8 -> 24 は 8 / (3 - 8 / 3) で、浮動小数点では 23.999... になり
    # 取りこぼす。Fraction による厳密計算では誤差なく見つかる。
    results = find_solutions("3 3 8 8", 24)
    assert "8 / (3 - 8 / 3)" in results
    assert all(evaluate_str(f) == 24 for f in results)


def test_target_parameter():
    results = find_solutions("1234", 24)
    assert results
    for formula in results:
        assert evaluate_str(formula) == 24


def test_no_dedup_yields_more():
    deduped = find_solutions("1234", 10, dedup=True)
    full = find_solutions("1234", 10, dedup=False)
    assert len(full) >= len(deduped)


def test_empty_input_returns_empty():
    assert find_solutions("", 10) == []


def evaluate_str(formula: str) -> Fraction:
    """表示文字列を Fraction で厳密に検算するヘルパ (浮動小数点を経由しない)."""
    expr = re.sub(r"\d+", lambda m: f"Fraction({m.group()})", formula)
    return eval(expr, {"Fraction": Fraction})  # noqa: S307  (テスト専用)
