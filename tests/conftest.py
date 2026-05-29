"""Shared pytest fixtures.

Every test runs against a fresh in-memory SQLite database (with foreign keys
enforced), so the suite is fast, isolated, and needs no external services.
GUI tests run under the offscreen Qt platform.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from bookshop.data.engine import Database
from bookshop.services.container import Container


@pytest.fixture
def database() -> Database:
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_all()
    try:
        yield db
    finally:
        db.dispose()


@pytest.fixture
def container(database: Database) -> Container:
    return Container(database)


@pytest.fixture
def services(container: Container):
    return container.services
