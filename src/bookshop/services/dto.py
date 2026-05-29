"""Data-transfer objects exchanged between services and the UI.

All DTOs are immutable (frozen) dataclasses holding only plain data, so they are
safe to pass between threads and never trigger lazy database loads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..core.money import format_money


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: int
    username: str
    role: str = "staff"


@dataclass(frozen=True, slots=True)
class BookDTO:
    id: int
    title: str
    author: str | None
    publisher: str | None
    isbn: str | None
    price_cents: int
    stock_qty: int

    @property
    def price_display(self) -> str:
        """Currency-formatted unit price (e.g. ``"$12.99"``)."""
        return format_money(self.price_cents)

    @property
    def in_stock(self) -> bool:
        """True when at least one unit is available."""
        return self.stock_qty > 0

    def status(self, low_stock_threshold: int) -> str:
        """Human-readable stock status given a low-stock threshold."""
        if self.stock_qty == 0:
            return "Out of stock"
        if self.stock_qty <= low_stock_threshold:
            return "Low stock"
        return "In stock"


@dataclass(frozen=True, slots=True)
class CartLine:
    """A request to sell *quantity* units of *book_id*."""

    book_id: int
    quantity: int = 1


@dataclass(frozen=True, slots=True)
class SaleItemDTO:
    book_id: int
    title: str
    quantity: int
    unit_price_cents: int
    line_total_cents: int

    @property
    def unit_price_display(self) -> str:
        return format_money(self.unit_price_cents)

    @property
    def line_total_display(self) -> str:
        return format_money(self.line_total_cents)


@dataclass(frozen=True, slots=True)
class SaleDTO:
    id: int
    total_cents: int
    created_at: datetime
    items: tuple[SaleItemDTO, ...] = field(default_factory=tuple)
    customer_name: str | None = None
    customer_phone: str | None = None
    sold_by: str | None = None

    @property
    def total_display(self) -> str:
        return format_money(self.total_cents)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass(frozen=True, slots=True)
class BookSalesDTO:
    book_id: int
    title: str
    quantity: int
    revenue_cents: int

    @property
    def revenue_display(self) -> str:
        return format_money(self.revenue_cents)


@dataclass(frozen=True, slots=True)
class DashboardDTO:
    total_titles: int
    total_stock_units: int
    low_stock_count: int
    today_revenue_cents: int
    today_units_sold: int
    month_revenue_cents: int

    @property
    def today_revenue_display(self) -> str:
        return format_money(self.today_revenue_cents)

    @property
    def month_revenue_display(self) -> str:
        return format_money(self.month_revenue_cents)
