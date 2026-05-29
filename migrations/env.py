"""Alembic migration environment.

The URL comes from the application settings, so the same migrations run against
SQLite (development/tests) and MySQL (production). ``render_as_batch`` is enabled
for SQLite so ``ALTER TABLE``-style operations work despite SQLite's limitations.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context

# Register all models on the metadata (import for side effects).
import bookshop.data.models  # noqa: E402,F401
from bookshop.data.base import Base
from bookshop.data.engine import make_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def run_migrations_offline() -> None:
    from bookshop.core.config import get_settings

    url = get_settings().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_is_sqlite(url),
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = make_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
