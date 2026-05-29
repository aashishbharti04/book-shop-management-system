"""Service layer: business rules, transactions, and DTOs.

Services are the only thing the presentation layer talks to. They accept a
session factory, own their transactions, and return immutable DTOs (never live
ORM objects), so database concerns never leak onto the UI thread.
"""

from __future__ import annotations

from .analytics_service import AnalyticsService
from .auth_service import AuthService
from .inventory_service import InventoryService
from .receipt_service import ReceiptService
from .sales_service import SalesService

__all__ = [
    "AnalyticsService",
    "AuthService",
    "InventoryService",
    "ReceiptService",
    "SalesService",
]
