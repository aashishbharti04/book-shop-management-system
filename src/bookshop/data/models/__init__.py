"""ORM models. Importing this package registers every model on the metadata."""

from __future__ import annotations

from .book import Book
from .sale import Sale, SaleItem
from .user import User

__all__ = ["Book", "Sale", "SaleItem", "User"]
