"""Guard that the schema compiles for both target dialects (MySQL & SQLite)."""

from __future__ import annotations

from sqlalchemy.dialects import mysql, sqlite
from sqlalchemy.schema import CreateTable

import bookshop.data.models  # noqa: F401  (registers tables on the metadata)
from bookshop.data.base import Base
from bookshop.data.models import Book


def test_every_table_compiles_for_both_dialects():
    for dialect in (mysql.dialect(), sqlite.dialect()):
        for table in Base.metadata.sorted_tables:
            ddl = str(CreateTable(table).compile(dialect=dialect))
            assert "CREATE TABLE" in ddl


def test_id_type_maps_per_dialect():
    """BigInteger PK renders as BIGINT on MySQL but INTEGER on SQLite (rowid)."""

    mysql_ddl = str(CreateTable(Book.__table__).compile(dialect=mysql.dialect()))
    sqlite_ddl = str(CreateTable(Book.__table__).compile(dialect=sqlite.dialect()))
    assert "BIGINT" in mysql_ddl
    assert "INTEGER" in sqlite_ddl


def test_check_constraints_present_in_ddl():
    ddl = str(CreateTable(Book.__table__).compile(dialect=sqlite.dialect()))
    assert "stock_qty >= 0" in ddl
