"""Money handling.

Money is represented everywhere as an integer number of **cents** to avoid the
floating-point rounding errors (and the ``eval(input())`` security hole) of the
legacy code. These helpers convert to/from the human-facing decimal form.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .config import get_settings
from .exceptions import ValidationError

_CLEAN_RE = re.compile(r"[,\s]")
_CURRENCY_SYMBOLS = "$€£₹"


def parse_money_to_cents(text: str | int | float) -> int:
    """Parse a user-entered amount into integer cents.

    Accepts strings like ``"12.50"``, ``"$1,299"`` or numbers. Rejects negative
    or malformed input with :class:`ValidationError`. This is the safe
    replacement for the legacy ``eval(input(...))``.
    """

    if isinstance(text, bool):  # bool is a subclass of int; reject explicitly
        raise ValidationError("Invalid price.")

    if isinstance(text, (int, float)):
        amount = Decimal(str(text))
    else:
        raw = _CLEAN_RE.sub("", str(text)).lstrip(_CURRENCY_SYMBOLS + get_settings().currency_symbol)
        if not raw:
            raise ValidationError("Price is required.")
        try:
            amount = Decimal(raw)
        except InvalidOperation as exc:
            raise ValidationError(f"'{text}' is not a valid amount.") from exc

    if amount < 0:
        raise ValidationError("Price cannot be negative.")
    # Quantize to 2 decimal places, then convert to integer cents.
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))


def cents_to_decimal_str(cents: int) -> str:
    """Return a plain two-decimal string, e.g. ``1250 -> "12.50"``."""

    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d}"


def format_money(cents: int, symbol: str | None = None) -> str:
    """Format cents as currency, e.g. ``1250 -> "$12.50"`` with thousands."""

    if symbol is None:
        symbol = get_settings().currency_symbol
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return f"{sign}{symbol}{whole:,}.{frac:02d}"
