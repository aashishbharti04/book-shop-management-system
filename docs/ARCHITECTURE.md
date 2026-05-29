# Architecture

Book Shop Management is a desktop application built with **PySide6 (Qt 6)** on a
clean, layered architecture. Each layer depends only on the ones beneath it, and
the UI never touches the database directly.

```
┌─────────────────────────────────────────────────────────────┐
│ presentation/  PySide6 — views, view-models, widgets, theme   │
│                async workers, navigation                      │
├─────────────────────────────────────────────────────────────┤
│ services/      business rules, transactions, DTOs             │
├─────────────────────────────────────────────────────────────┤
│ data/          SQLAlchemy models, repositories, engine        │
├─────────────────────────────────────────────────────────────┤
│ core/          config, security, logging, money, exceptions   │
└─────────────────────────────────────────────────────────────┘
        MySQL (production)  ·  SQLite (dev / tests)
```

## Layers

### `core`
Cross-cutting fundamentals with no dependencies on the rest of the app:
- **config** — immutable `Settings` read once from the environment / `.env`.
- **security** — bcrypt hashing/verification and the password policy (all bcrypt
  byte-handling lives here).
- **money** — integer-cents parsing/formatting (replaces the legacy `eval()`).
- **exceptions** — the domain error hierarchy raised by services.
- **logging** — one-time logging configuration.

### `data`
- **models** — `User`, `Book`, `Sale`, `SaleItem` as SQLAlchemy ORM classes.
  Identifiers use a `BigInteger` that renders as `INTEGER` on SQLite (so primary
  keys remain rowid-autoincrement) and `BIGINT` on MySQL.
- **engine** — builds the engine + session factory, turns on SQLite foreign-key
  enforcement, and exposes `session_scope` (commit/rollback/close).
- **repositories** — the only place SQL is written. Each wraps one `Session`.

### `services`
Business rules and transaction boundaries. Services accept a session factory,
open their own unit of work, and **return frozen-dataclass DTOs** — never live
ORM objects. This keeps lazy-loading and detached-instance issues away from the
UI thread.

Key invariants enforced here:
- **Atomic sales** — `SalesService.create_sale` decrements stock with a guarded
  `UPDATE … WHERE stock_qty >= qty`; if any line lacks stock the whole sale rolls
  back. The unit price is captured at sale time.
- **Scoped updates** — `InventoryService.update_book` only ever touches one row.
- **Correct analytics** — period queries use a half-open `[start, end)` range.

### `presentation`
PySide6 UI following **MVVM**:
- **views** — `QWidget`s that only build layout and bind signals.
- **viewmodels** — `QObject`s holding UI state; they call services exclusively
  through the worker layer and expose Qt signals (`busyChanged`, `…Loaded`,
  `errorOccurred`).
- **widgets** — the in-app design system (buttons, card, data table, toast,
  skeleton, empty/error states, spinner/overlay, form field).
- **theme** — design tokens compiled into a Qt stylesheet; dark/light with a
  runtime switch persisted via `QSettings`.
- **workers** — a `QThreadPool` + `Worker(QRunnable)`/`WorkerSignals` and a
  `TaskRunner`. A `SyncTaskRunner` test double runs callables inline.

## Threading model

Database work runs on a background thread pool so the UI never freezes:

```
View → ViewModel → TaskRunner.run(service_call)
                        │  (worker thread: opens its OWN Session, returns a DTO)
                        ▼
        WorkerSignals.result/error  ──(queued, cross-thread)──▶  ViewModel slot → View
```

Each worker task opens a fresh `Session` (sessions are not thread-safe) and
returns DTOs, which are safe to hand back to the GUI thread.

## Data model

```
User 1──* Sale 1──* SaleItem *──1 Book
```

- `Book` — `price_cents`, `stock_qty` (with `CHECK (stock_qty >= 0)`), ISBN, etc.
- `Sale` — receipt header: customer, total, cashier, timestamp.
- `SaleItem` — line item with `quantity` and `unit_price_cents` captured at sale
  time, so later price edits never rewrite history.

## Database portability

The same SQLAlchemy models and Alembic migrations target both MySQL (production)
and SQLite (dev/tests). Migrations run in **batch mode** so `ALTER TABLE`
operations work under SQLite, and a unit test compiles the schema for both
dialects to catch any incompatibility.

## Testing

- **Unit tests** run against an in-memory SQLite database and cover services,
  repositories, security, money, analytics correctness, and schema portability.
- **GUI smoke tests** use `pytest-qt` with the offscreen Qt platform and inject
  the `SyncTaskRunner` for deterministic async behavior.
