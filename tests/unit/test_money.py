from __future__ import annotations

import pytest

from bookshop.core.exceptions import ValidationError
from bookshop.core.money import cents_to_decimal_str, format_money, parse_money_to_cents


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12.50", 1250),
        ("12", 1200),
        ("$1,299.00", 129900),
        ("0.99", 99),
        (5, 500),
        (9.99, 999),
        ("  7.5 ", 750),
    ],
)
def test_parse_money_to_cents(value, expected):
    assert parse_money_to_cents(value) == expected


@pytest.mark.parametrize("bad", ["", "abc", "12.3.4", "$$", "ten"])
def test_parse_money_rejects_garbage(bad):
    with pytest.raises(ValidationError):
        parse_money_to_cents(bad)


def test_parse_money_rejects_negative():
    with pytest.raises(ValidationError):
        parse_money_to_cents("-5.00")


def test_parse_money_rejects_bool():
    with pytest.raises(ValidationError):
        parse_money_to_cents(True)


def test_format_and_decimal_helpers():
    assert format_money(1250, symbol="$") == "$12.50"
    assert format_money(129900, symbol="$") == "$1,299.00"
    assert format_money(-500, symbol="$") == "-$5.00"
    assert cents_to_decimal_str(1250) == "12.50"
    assert cents_to_decimal_str(5) == "0.05"
