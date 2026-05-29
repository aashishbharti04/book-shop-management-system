"""Command-line entry point: ``python -m bookshop`` (or the ``bookshop`` script).

Subcommands:

* ``run``    — launch the desktop application (default).
* ``initdb`` — create the database schema.
* ``seed``   — populate the database with demo data.
* ``info``   — print application / environment information.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__

_BANNER = r"""
  ____              _      ____  _
 | __ )  ___   ___ | | __ / ___|| |__   ___  _ __
 |  _ \ / _ \ / _ \| |/ / \___ \| '_ \ / _ \| '_ \
 | |_) | (_) | (_) |   <   ___) | | | | (_) | |_) |
 |____/ \___/ \___/|_|\_\ |____/|_| |_|\___/| .__/
                                            |_|     Management
"""


def _info() -> int:
    from .core.config import get_settings

    settings = get_settings()
    backend = (
        "SQLite (local file)" if settings.is_sqlite else settings.database_url.split("://", 1)[0]
    )
    print(_BANNER)
    print(f"  version        : {__version__}")
    print(f"  app name       : {settings.app_name}")
    print(f"  database       : {backend}")
    print(f"  theme          : {settings.default_theme}")
    print(f"  font scale     : {settings.font_scale}")
    print(f"  reduced motion : {settings.reduced_motion}")
    return 0


def _initdb() -> int:
    from .core.logging import get_logger
    from .data.engine import Database

    Database().create_all()
    get_logger("bookshop.cli").info("Database schema created.")
    print("Database schema created.")
    return 0


def _seed(*, reset: bool) -> int:
    from .services.seed import seed_demo_data

    summary = seed_demo_data(reset=reset)
    print(summary)
    return 0


def _run() -> int:
    try:
        from .app import run
    except ImportError as exc:  # pragma: no cover - environment dependent
        print(f"Unable to launch the GUI: {exc}", file=sys.stderr)
        print("Install dependencies with: pip install -e .", file=sys.stderr)
        return 1
    return run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bookshop",
        description="Book Shop Management — desktop application and tools.",
    )
    parser.add_argument("--version", action="version", version=f"bookshop {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Launch the desktop application (default).")
    sub.add_parser("initdb", help="Create the database schema.")
    seed_parser = sub.add_parser("seed", help="Populate the database with demo data.")
    seed_parser.add_argument(
        "--reset", action="store_true", help="Drop and recreate all tables first."
    )
    sub.add_parser("info", help="Print application and environment information.")

    args = parser.parse_args(argv)
    command = args.command or "run"

    if command == "info":
        return _info()
    if command == "initdb":
        return _initdb()
    if command == "seed":
        return _seed(reset=bool(getattr(args, "reset", False)))
    return _run()


if __name__ == "__main__":
    raise SystemExit(main())
