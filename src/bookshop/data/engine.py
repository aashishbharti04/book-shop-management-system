"""Engine and session management.

The :class:`Database` bundles a SQLAlchemy engine with a session factory and a
transactional ``session_scope`` context manager. Each unit of work (including
every background worker task) obtains its **own** short-lived session — sessions
are not safe to share across threads.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..core.config import get_settings

# Import models so they are registered on ``Base.metadata`` before create_all().
from . import models as _models  # noqa: F401  (side-effect import)
from .base import Base


def make_engine(url: str | None = None, *, echo: bool = False, **kwargs: Any) -> Engine:
    """Create a configured engine for *url* (defaults to the settings URL)."""

    url = url or get_settings().database_url
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {"future": True, "echo": echo, "pool_pre_ping": True}

    if url.startswith("sqlite"):
        # Allow cross-thread use (each thread still uses its own Session).
        connect_args["check_same_thread"] = False
        # A shared in-memory database must keep a single connection alive.
        if ":memory:" in url or url in ("sqlite://", "sqlite:///:memory:"):
            engine_kwargs["poolclass"] = StaticPool
            engine_kwargs.pop("pool_pre_ping", None)

    engine_kwargs.update(kwargs)
    engine = create_engine(url, connect_args=connect_args, **engine_kwargs)

    if engine.dialect.name == "sqlite":
        _enable_sqlite_foreign_keys(engine)
    return engine


@contextmanager
def session_scope(session_factory: sessionmaker) -> Iterator[Session]:
    """Yield a session that commits on success and rolls back on error.

    This is the single transaction boundary used by every service method and
    every background worker task; each call gets its own short-lived session.
    """

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """SQLite does not enforce foreign keys unless asked to, per connection."""

    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_connection: Any, _record: Any) -> None:  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Database:
    """Owns the engine and hands out transactional sessions."""

    def __init__(self, url: str | None = None, *, echo: bool = False, **kwargs: Any) -> None:
        self.engine = make_engine(url, echo=echo, **kwargs)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            future=True,
            class_=Session,
        )

    def create_all(self) -> None:
        """Create all tables (used for dev/test bootstrapping)."""

        Base.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        Base.metadata.drop_all(self.engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Yield a session that commits on success and rolls back on error."""

        with session_scope(self.session_factory) as session:
            yield session

    def dispose(self) -> None:
        self.engine.dispose()
