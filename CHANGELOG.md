# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete rebuild of the legacy CLI into a **PySide6 desktop application** with
  a layered architecture (core / data / services / presentation).
- Dark and light themes with a runtime toggle, smooth animations, skeleton
  loaders, and dedicated empty / error states.
- Accessibility: keyboard navigation, screen-reader labels, adjustable font
  scale, and a reduced-motion mode.
- Inventory management, point-of-sale with atomic stock decrement, cross-platform
  receipt printing / PDF export, and an analytics dashboard with an embedded
  monthly-sales chart.
- SQLAlchemy data layer supporting **MySQL** (production) and **SQLite**
  (zero-config dev/test), with Alembic migrations.
- Test suite (pytest + pytest-qt) and CI (ruff, mypy, pytest).
- A persistent in-app footer with maintainer contact and social links.
- Open-source community files: `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue/feature
  templates, and a pull-request template.
- Expanded CI into separate **lint / type-check / test / build / deploy-ready**
  jobs plus a MySQL-parity job.
- Documentation: folder structure, development, deployment, user manual, and a
  service-layer API reference.

### Changed
- View-model signals now carry concrete DTO types (removing `object` casts).
- Dashboard low-stock count now uses a scalar `COUNT` query (was hydrating rows).
- The analytics chart only re-styles when visible, avoiding redundant redraws.
- Stock-status logic moved onto `BookDTO.status()` for reuse.
- `utcnow` moved to `core.clock` so the presentation layer no longer imports
  from the data layer.

### Security
- Passwords are now hashed with **bcrypt** (previously stored in plain text).
- All queries are parameterized via the ORM (eliminates the legacy SQL injection).
- Database credentials moved out of source code into environment configuration.
- Removed `eval()`-based numeric input.

### Fixed
- `update_stock` no longer updates every row (now scoped by book id).
- Monthly sales analytics now count per-period quantities correctly.
- Selling is atomic and can never drive stock negative.
