"""Domain-level exception hierarchy.

Services raise these (never raw SQLAlchemy errors) so the presentation layer can
map them to friendly, user-facing messages.
"""

from __future__ import annotations


class BookShopError(Exception):
    """Base class for all application errors."""


class ValidationError(BookShopError):
    """Raised when user-supplied input fails validation."""


class PasswordPolicyError(ValidationError):
    """Raised when a password does not meet the security policy."""


class AuthError(BookShopError):
    """Base class for authentication failures."""


class UsernameTakenError(AuthError):
    """Raised when registering a username that already exists."""


class InvalidCredentialsError(AuthError):
    """Raised when a login attempt fails."""


class NotFoundError(BookShopError):
    """Raised when a requested entity does not exist."""


class OutOfStockError(BookShopError):
    """Raised when a sale requests more units than are available."""

    def __init__(self, book_id: int, requested: int, available: int) -> None:
        self.book_id = book_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for book {book_id}: "
            f"requested {requested}, only {available} available."
        )
