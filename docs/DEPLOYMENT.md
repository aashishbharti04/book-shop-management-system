# Deployment guide

Book Shop Management is a **desktop application**. "Deployment" means installing
it on the machines that will run it and (optionally) pointing it at a shared
MySQL database.

## 1. Choose a database

| Mode | When | `DATABASE_URL` |
|------|------|----------------|
| **SQLite** (default) | Single machine, single user | _unset_ → `sqlite:///bookshop.db` |
| **MySQL** | Shared catalogue across machines | `mysql+pymysql://user:pass@host:3306/book_shop` |

Configure via environment variables or a `.env` file (see [`.env.example`](../.env.example)).

## 2. Production MySQL setup

Bring up MySQL (the bundled Compose file is a convenient start):

```bash
docker-compose up -d        # MySQL 8 on :3306, Adminer on :8080
```

Or use a managed MySQL. Then create the schema:

```bash
export DATABASE_URL="mysql+pymysql://bookshop:STRONG_PASSWORD@db-host:3306/book_shop"
alembic upgrade head
```

**Security hardening for production MySQL:**
- Use a dedicated DB user with only the privileges it needs (no `GRANT ALL`).
- Require TLS for the connection and rotate credentials periodically.
- Never commit `.env`; inject secrets via the OS environment or a secrets manager.
- Take regular backups (`mysqldump`) before upgrading.

## 3. Install the app on a workstation

### From source

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate
pip install .
bookshop initdb      # only needed for SQLite; for MySQL run alembic upgrade head
bookshop             # launch
```

### As a built wheel

```bash
python -m build              # produces dist/bookshop-*.whl
pip install dist/bookshop-*.whl
bookshop
```

### As a standalone executable (optional)

You can freeze a single-file binary with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --name BookShop --windowed --onefile -m bookshop
```

The executable lands in `dist/`. Bundle a `.env` (or set env vars) so it can
find the database.

## 4. Upgrading

1. Back up the database (copy `bookshop.db`, or `mysqldump` for MySQL).
2. Install the new version.
3. Run `alembic upgrade head` to apply any new migrations.
4. Launch and verify. Migration notes for breaking changes are recorded in
   [`CHANGELOG.md`](../CHANGELOG.md).

## 5. CI deployment-ready checks

Every push runs the `build` and `deploy-ready` jobs in
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml): they build the
sdist/wheel, validate metadata with `twine`, install the wheel into a clean
environment, and smoke-test the `bookshop` console script.
