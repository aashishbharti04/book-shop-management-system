"""Declarative base and shared column helpers.

A constraint *naming convention* is configured so every index, unique,
check and foreign-key constraint gets a deterministic name. Alembic needs this
to emit ``ALTER``-style migrations that also work under SQLite's batch mode.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Integer, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TypeEngine

from ..core.clock import utcnow  # re-exported so models can import it from here

__all__ = ["Base", "id_type", "metadata", "utcnow"]

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


def id_type() -> TypeEngine:
    """Identifier column type that is portable across MySQL and SQLite.

    Renders as ``BIGINT`` on MySQL but as plain ``INTEGER`` on SQLite, so that a
    primary key still maps to SQLite's autoincrementing ``rowid``.
    """

    return BigInteger().with_variant(Integer, "sqlite")
