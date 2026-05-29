"""A tiny dependency-injection container.

Builds the :class:`~bookshop.data.engine.Database` and constructs every service
against its session factory, exactly once. Shared by the GUI, the CLI, and tests
(tests pass an in-memory ``Database``).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..data.engine import Database
from .analytics_service import AnalyticsService
from .auth_service import AuthService
from .inventory_service import InventoryService
from .receipt_service import ReceiptService
from .sales_service import SalesService


@dataclass(frozen=True)
class Services:
    auth: AuthService
    inventory: InventoryService
    sales: SalesService
    analytics: AnalyticsService
    receipts: ReceiptService


class Container:
    def __init__(self, database: Database | None = None) -> None:
        self.database: Database = database if database is not None else Database()
        session_factory = self.database.session_factory
        self.services = Services(
            auth=AuthService(session_factory),
            inventory=InventoryService(session_factory),
            sales=SalesService(session_factory),
            analytics=AnalyticsService(session_factory),
            receipts=ReceiptService(),
        )

    def dispose(self) -> None:
        self.database.dispose()
