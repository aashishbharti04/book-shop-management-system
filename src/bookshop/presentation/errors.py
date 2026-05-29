"""Map exceptions to user-facing messages for the UI."""

from __future__ import annotations

from ..core.exceptions import BookShopError


def humanize_error(exc: BaseException) -> str:
    if isinstance(exc, BookShopError):
        return str(exc)
    return "An unexpected error occurred. Please try again."
