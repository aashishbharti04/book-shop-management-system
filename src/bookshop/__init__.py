"""Book Shop Management — a modern desktop book-shop management application.

The package is organized in layers:

* :mod:`bookshop.core` — configuration, security, logging, domain exceptions.
* :mod:`bookshop.data` — SQLAlchemy models, engine/session factory, repositories.
* :mod:`bookshop.services` — business logic and data-transfer objects (DTOs).
* :mod:`bookshop.presentation` — the PySide6 user interface (MVVM).
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
