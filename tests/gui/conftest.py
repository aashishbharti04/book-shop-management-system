from __future__ import annotations

import pytest

from bookshop.data.engine import Database
from bookshop.presentation.context import AppContext
from bookshop.presentation.theme import ThemeManager
from bookshop.presentation.workers import SyncTaskRunner
from bookshop.services.container import Container


@pytest.fixture
def app_context(qapp):
    """An AppContext backed by an in-memory DB and a synchronous task runner."""

    db = Database("sqlite+pysqlite:///:memory:")
    db.create_all()
    container = Container(db)
    theme = ThemeManager(qapp, persist=False)
    theme.apply()
    ctx = AppContext(container.services, theme, SyncTaskRunner())
    try:
        yield ctx
    finally:
        db.dispose()
