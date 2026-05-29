"""Repositories: the only place that builds SQL queries.

Each repository wraps a single :class:`~sqlalchemy.orm.Session`. Services own the
transaction (via ``session_scope``) and pass the session to repositories.
"""

from __future__ import annotations

from .book_repository import BookRepository
from .sale_repository import SaleRepository
from .user_repository import UserRepository

__all__ = ["BookRepository", "SaleRepository", "UserRepository"]
