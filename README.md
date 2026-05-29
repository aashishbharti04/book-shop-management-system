<div align="center">

# 📚 Book Shop Management

**A modern, production-ready desktop application for running a book shop —
inventory, point-of-sale, and sales analytics.**

Built with **PySide6 (Qt 6)** · **SQLAlchemy** · **MySQL / SQLite** · **matplotlib**

[![CI](https://github.com/aashishbharti04/book-shop-management-system/actions/workflows/ci.yml/badge.svg)](https://github.com/aashishbharti04/book-shop-management-system/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![Typed: mypy](https://img.shields.io/badge/typed-mypy-blue.svg)](https://mypy-lang.org/)

</div>

---

## 📖 Overview

Book Shop Management is a complete, modern rebuild of a legacy command-line
book-shop program. It keeps **every original feature** — user accounts, stock
management, selling books with printed receipts, and monthly sales charts — and
rebuilds them as a polished, accessible **desktop app** with a clean layered
architecture, a full test suite, and CI.

It runs out of the box on a zero-config local **SQLite** database and scales to
**MySQL** for shared, production use.

> The original CLI source is preserved under [`legacy/`](legacy/) for reference.

## ✨ Features

- **Accounts & authentication** — register and sign in; passwords are hashed with
  **bcrypt** (never stored in plain text).
- **Inventory management** — add, search, sort, edit, and restock books;
  out-of-stock items are flagged, never silently deleted.
- **Point of sale** — build a multi-line cart, sell **atomically** (stock can
  never go negative), and generate a cross-platform receipt you can **print or
  export to PDF**.
- **Analytics dashboard** — at-a-glance KPIs plus a monthly sales bar chart
  rendered with matplotlib **embedded directly in the window**.
- **Premium UX** — dark & light themes, smooth animations, skeleton loaders, and
  dedicated empty / error states.
- **Accessible** — full keyboard navigation, screen-reader labels, adjustable
  font scale, and a reduced-motion mode.
- **Responsive** — layouts adapt fluidly from compact to wide windows.

## 📸 Screenshots

| Sign in | Dashboard |
|---|---|
| ![Sign in](docs/screenshots/auth_dark.png) | ![Dashboard](docs/screenshots/dashboard_dark.png) |

| Inventory | Point of sale |
|---|---|
| ![Inventory](docs/screenshots/inventory_dark.png) | ![Sell](docs/screenshots/sell_dark.png) |

| Analytics | Settings |
|---|---|
| ![Analytics](docs/screenshots/analytics_dark.png) | ![Settings](docs/screenshots/settings_dark.png) |

<div align="center"><sub>Light theme</sub><br><img src="docs/screenshots/dashboard_light.png" width="640" alt="Dashboard in light theme"></div>

## 🚀 Installation

> Requires **Python 3.12+**. No database server is needed for the default
> setup — it uses a zero-config local SQLite file.

```bash
# 1. Clone
git clone https://github.com/aashishbharti04/book-shop-management-system.git
cd book-shop-management-system

# 2. Create & activate a virtual environment
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

# 3. Install (editable, with dev tools)
pip install -e ".[dev]"

# 4. Create the database schema
python -m bookshop initdb        # or: alembic upgrade head

# 5. (Optional) load demo data — creates account demo / demo1234
python -m bookshop seed

# 6. Launch
python -m bookshop
```

## 🧭 Usage

Once launched:

1. **Create an account** (or use `demo` / `demo1234` after seeding) and sign in.
2. **Dashboard** — see today's revenue, units sold, stock levels, and recent sales.
3. **Inventory** — add / search / sort / edit / restock books.
4. **Sell** — build a cart, complete the sale, then **print** or **save the
   receipt as PDF**.
5. **Analytics** — pick a month to view the sales chart and top sellers.
6. **Settings** — switch theme, text size, or enable reduced motion.

Full walkthrough with screenshots: [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md).

The CLI also offers:

```bash
python -m bookshop --version    # version
python -m bookshop info         # app & environment info
python -m bookshop initdb       # create tables
python -m bookshop seed --reset # drop, recreate, and re-seed
```

## ⚙️ Configuration

All configuration is via environment variables (a `.env` file is loaded if
present). Copy [`.env.example`](.env.example) to `.env` to start.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///bookshop.db` | SQLAlchemy URL. MySQL: `mysql+pymysql://user:pass@host:3306/book_shop` |
| `APP_NAME` | `Book Shop Management` | Window title / QSettings scope |
| `ORG_NAME` | `BookShopOSS` | QSettings org scope |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `BOOKSHOP_THEME` | `dark` | `dark` / `light` |
| `BOOKSHOP_FONT_SCALE` | `medium` | `small` / `medium` / `large` |
| `BOOKSHOP_REDUCED_MOTION` | `0` | `1` to disable animations |
| `BOOKSHOP_CURRENCY` | `$` | Currency symbol |
| `BOOKSHOP_LOW_STOCK_THRESHOLD` | `5` | Units at/below which a title is "low stock" |

Secrets (`.env`, `*.db`) are git-ignored — never commit them.

## 🐬 Deployment

Run against MySQL for shared/production use:

```bash
docker-compose up -d        # local MySQL 8 + Adminer (http://localhost:8080)
export DATABASE_URL="mysql+pymysql://bookshop:bookshop@localhost:3306/book_shop"
alembic upgrade head
python -m bookshop
```

Build a wheel or a standalone executable, harden production MySQL, and upgrade
safely — see [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## 🧱 Architecture

A clean, testable, layered design (`presentation → services → data → core`):

```
src/bookshop/
├── core/           # config, security (bcrypt), money, clock, logging, exceptions
├── data/           # SQLAlchemy models, repositories, engine/session factory
├── services/       # business logic (auth, inventory, sales, analytics, receipts) + DTOs
└── presentation/   # PySide6 — views, view-models (MVVM), widgets, theme, workers
```

- **Services return DTOs**, never live ORM objects — database concerns stay off
  the UI thread.
- **Database work runs on a worker thread pool** and feeds loading / skeleton
  states, so the UI never freezes.
- **Money is stored as integer cents** end-to-end to avoid floating-point error.

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/FOLDER_STRUCTURE.md`](docs/FOLDER_STRUCTURE.md) ·
[`docs/SERVICES.md`](docs/SERVICES.md).

## 🧪 Development & Contributing

```bash
pip install -e ".[dev]"
pytest                 # unit + offscreen GUI tests
ruff check .           # lint
mypy                   # type-check
```

GUI tests run headless via `QT_QPA_PLATFORM=offscreen`. See
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) and
[`CONTRIBUTING.md`](CONTRIBUTING.md). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md) and report vulnerabilities per
[`SECURITY.md`](SECURITY.md).

## ❓ FAQ

<details>
<summary><b>Do I need MySQL to run it?</b></summary>

No. By default it uses a local SQLite file (`bookshop.db`) with zero setup.
MySQL is optional, for shared/production use.
</details>

<details>
<summary><b>Where is my data stored?</b></summary>

In `bookshop.db` in the project directory (SQLite), or in your MySQL database if
`DATABASE_URL` points there.
</details>

<details>
<summary><b>I forgot the demo password.</b></summary>

It's `demo` / `demo1234` (created by `python -m bookshop seed`). For a fresh
start, delete `bookshop.db` and re-run `initdb` + `seed`.
</details>

<details>
<summary><b>Is this a web app?</b></summary>

No — it's a cross-platform **desktop** application (PySide6/Qt). It runs on
Windows, macOS, and Linux.
</details>

<details>
<summary><b>Screenshots show boxes instead of text?</b></summary>

That only happens when rendering under the headless "offscreen" Qt platform
(used in CI). The app renders normally on a real display.
</details>

## 📄 License

Released under the [MIT License](LICENSE).

---

<div align="center">

### 👤 Maintainer & Contact

**aashishbharti04**

[📧 Email](mailto:aashish@marketdoctorsonline.com) ·
[💼 LinkedIn](https://in.linkedin.com/in/aashana1012) ·
[🐙 GitHub](https://github.com/aashishbharti04) ·
[▶️ YouTube](https://www.youtube.com/@CodeWithAsur) ·
[📸 Instagram](https://www.instagram.com/asurwave1012?igsh=ZDBlY2NtczJ5cmMw)

© 2026 Book Shop Management. All rights reserved.

_This project is open source and available for educational, learning, and community contributions._

</div>
