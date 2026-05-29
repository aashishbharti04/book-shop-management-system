# Contributing

Thanks for your interest in improving Book Shop Management! This guide gets you
from clone to green tests.

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
python -m bookshop initdb
python -m bookshop seed      # optional demo data
```

## Project layout

| Layer | Path | Responsibility |
|-------|------|----------------|
| Core | `src/bookshop/core` | Config, security, logging, exceptions |
| Data | `src/bookshop/data` | ORM models, engine/session, repositories |
| Services | `src/bookshop/services` | Business rules, transactions, DTOs |
| Presentation | `src/bookshop/presentation` | PySide6 views, view-models, widgets, theme |

**Golden rules**

- The presentation layer talks to **services**, never to repositories or the ORM
  directly.
- Services accept a session factory and own their transactions; they return
  **frozen-dataclass DTOs**, not ORM instances.
- All database calls from the UI go through the **worker/`TaskRunner`** so the UI
  thread never blocks.
- Money is **integer cents**. Format to currency only at the view edge.

## Running checks

```bash
pytest                 # all tests (GUI tests run offscreen automatically)
ruff check .           # lint
ruff format .          # auto-format
mypy                   # type-check
```

Please run `pre-commit install` so lint/format run on every commit:

```bash
pip install pre-commit && pre-commit install
```

## Tests

- Unit tests live in `tests/unit/` and run against an **in-memory SQLite**
  database (see `tests/conftest.py`).
- GUI smoke tests live in `tests/gui/` and use `pytest-qt` with the offscreen
  Qt platform. Inject the `SyncTaskRunner` test double for deterministic async.
- New behavior should ship with tests. Bug fixes should add a regression test.

## Database migrations

When you change a model, generate a migration:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

Migrations use **batch mode** so they apply on SQLite as well as MySQL.

## Commit / PR

- Keep changes focused; describe the "why" in the PR.
- Ensure `pytest`, `ruff`, and `mypy` pass.
- Update `CHANGELOG.md` under "Unreleased".
