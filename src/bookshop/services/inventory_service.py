"""Inventory management: add, edit, restock, search and list books."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from ..core.exceptions import NotFoundError, ValidationError
from ..data.models import Book
from ..data.repositories import BookRepository
from .base import BaseService, to_book_dto
from .dto import BookDTO

_EDITABLE_FIELDS = {"title", "author", "publisher", "isbn", "price_cents"}


def _clean_optional(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class InventoryService(BaseService):
    def add_book(
        self,
        *,
        title: str,
        price_cents: int,
        author: str | None = None,
        publisher: str | None = None,
        isbn: str | None = None,
        initial_qty: int = 0,
    ) -> BookDTO:
        title = (title or "").strip()
        if not title:
            raise ValidationError("Title is required.")
        if price_cents < 0:
            raise ValidationError("Price cannot be negative.")
        if initial_qty < 0:
            raise ValidationError("Initial quantity cannot be negative.")

        isbn = _clean_optional(isbn)
        with self._unit_of_work() as session:
            repo = BookRepository(session)
            if isbn and repo.get_by_isbn(isbn) is not None:
                raise ValidationError(f"A book with ISBN '{isbn}' already exists.")
            book = Book(
                title=title,
                author=_clean_optional(author),
                publisher=_clean_optional(publisher),
                isbn=isbn,
                price_cents=price_cents,
                stock_qty=initial_qty,
            )
            try:
                repo.add(book)
            except IntegrityError as exc:
                raise ValidationError(f"A book with ISBN '{isbn}' already exists.") from exc
            return to_book_dto(book)

    def update_book(self, book_id: int, **fields: object) -> BookDTO:
        """Update a *single* book, scoped strictly by id.

        Fixes the legacy bug where ``update_stock`` updated every row because it
        had no ``WHERE`` clause.
        """

        updates = {key: value for key, value in fields.items() if key in _EDITABLE_FIELDS}
        if not updates:
            raise ValidationError("No valid fields to update.")

        if "title" in updates and not str(updates["title"] or "").strip():
            raise ValidationError("Title is required.")
        price = updates.get("price_cents")
        if price is not None and (not isinstance(price, int) or price < 0):
            raise ValidationError("Price cannot be negative.")

        with self._unit_of_work() as session:
            repo = BookRepository(session)
            book = repo.get(book_id)
            if book is None:
                raise NotFoundError(f"Book {book_id} does not exist.")

            new_isbn = _clean_optional(updates.get("isbn"))
            if "isbn" in updates and new_isbn and new_isbn != book.isbn:
                existing = repo.get_by_isbn(new_isbn)
                if existing is not None and existing.id != book_id:
                    raise ValidationError(f"A book with ISBN '{new_isbn}' already exists.")

            for key, value in updates.items():
                if key == "title":
                    value = str(value).strip()
                elif key in {"author", "publisher", "isbn"}:
                    value = _clean_optional(value)
                setattr(book, key, value)
            session.flush()
            return to_book_dto(book)

    def restock(self, book_id: int, quantity: int) -> BookDTO:
        if quantity <= 0:
            raise ValidationError("Restock quantity must be positive.")
        with self._unit_of_work() as session:
            book = BookRepository(session).get(book_id)
            if book is None:
                raise NotFoundError(f"Book {book_id} does not exist.")
            book.stock_qty += quantity
            session.flush()
            return to_book_dto(book)

    def get_book(self, book_id: int) -> BookDTO:
        with self._unit_of_work() as session:
            book = BookRepository(session).get(book_id)
            if book is None:
                raise NotFoundError(f"Book {book_id} does not exist.")
            return to_book_dto(book)

    def list_books(
        self,
        *,
        search: str | None = None,
        sort_by: str = "title",
        order: str = "asc",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[BookDTO]:
        with self._unit_of_work() as session:
            books = BookRepository(session).list_all(
                search=search, sort_by=sort_by, order=order, limit=limit, offset=offset
            )
            return [to_book_dto(book) for book in books]

    def count_books(self, search: str | None = None) -> int:
        with self._unit_of_work() as session:
            return BookRepository(session).count(search=search)
