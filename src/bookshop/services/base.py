"""Base class for services and shared ORM-to-DTO mappers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker

from ..data.engine import session_scope
from ..data.models import Book, Sale, User
from .dto import BookDTO, SaleDTO, SaleItemDTO, UserDTO


class BaseService:
    """Holds the session factory and exposes the transactional ``_unit_of_work``."""

    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _unit_of_work(self) -> Iterator[Session]:
        with session_scope(self._session_factory) as session:
            yield session


def to_user_dto(user: User) -> UserDTO:
    return UserDTO(id=user.id, username=user.username, role=user.role)


def to_book_dto(book: Book) -> BookDTO:
    return BookDTO(
        id=book.id,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        isbn=book.isbn,
        price_cents=book.price_cents,
        stock_qty=book.stock_qty,
    )


def to_sale_dto(sale: Sale, items: tuple[SaleItemDTO, ...]) -> SaleDTO:
    return SaleDTO(
        id=sale.id,
        total_cents=sale.total_cents,
        created_at=sale.created_at,
        items=items,
        customer_name=sale.customer_name,
        customer_phone=sale.customer_phone,
        sold_by=sale.sold_by.username if sale.sold_by is not None else None,
    )
