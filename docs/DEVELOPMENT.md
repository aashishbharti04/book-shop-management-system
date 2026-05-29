# Development setup guide

## Prerequisites

- **Python 3.12+** (3.12 or 3.13 recommended; the app also runs on 3.14).
- Git.
- Optional: Docker (for the local MySQL service).

## First-time setup

```bash
git clone https://github.com/aashishbharti04/book-shop-management-system.git
cd book-shop-management-system

python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

pip install -e ".[dev]"      # editable install with dev tools
python -m bookshop initdb    # create the SQLite schema
python -m bookshop seed      # optional demo data (demo / demo1234)
python -m bookshop           # launch the app
```

## Everyday commands

| Task | Command |
|------|---------|
| Run the app | `python -m bookshop` |
| Print app/env info | `python -m bookshop info` |
| Create schema | `python -m bookshop initdb` |
| Seed demo data | `python -m bookshop seed [--reset]` |
| Run tests | `pytest` |
| Lint | `ruff check .` |
| Auto-format | `ruff format .` |
| Type-check | `mypy` |
| New migration | `alembic revision --autogenerate -m "..."` |
| Apply migrations | `alembic upgrade head` |

## Pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks run ruff (lint + format) and basic hygiene checks on every commit.

## Testing

- **Unit tests** (`tests/unit/`) run against an in-memory SQLite database — fast
  and isolated.
- **GUI tests** (`tests/gui/`) use `pytest-qt` with the **offscreen** Qt platform
  (no display needed). The `app_context` fixture wires services to an in-memory
  DB and a synchronous `SyncTaskRunner` for deterministic async behavior.
- A threaded-runner regression test (`tests/gui/test_task_runner.py`) exercises
  the real `QThreadPool` path.

Run a subset:

```bash
pytest tests/unit                 # logic only, no Qt
QT_QPA_PLATFORM=offscreen pytest tests/gui
```

> On Windows the offscreen platform may render text as boxes in screenshots —
> that's a headless-font artifact, not a bug. The app renders normally on a real
> display.

## Testing against MySQL locally

```bash
docker-compose up -d
export DATABASE_URL="mysql+pymysql://bookshop:bookshop@localhost:3306/book_shop"
alembic upgrade head
pytest
```

## Debugging tips

- Set `LOG_LEVEL=DEBUG` in `.env` for verbose logs.
- Background DB work runs on a thread pool; UI updates always happen on the GUI
  thread via signals. If a screen never updates, check that the view-model
  signal is connected and the worker isn't raising (errors are logged).
- Set `BOOKSHOP_REDUCED_MOTION=1` to disable animations while debugging layout.
