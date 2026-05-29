# Folder structure

```
book-shop-management-system/
├── .github/
│   ├── ISSUE_TEMPLATE/         # bug report, feature request, config
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/ci.yml        # lint · typecheck · test · mysql · build · deploy-ready
├── assets/
│   ├── fonts/  icons/  qss/    # bundled assets (themes are generated in code)
├── docs/
│   ├── ARCHITECTURE.md         # layered design, threading, data model
│   ├── FOLDER_STRUCTURE.md     # this file
│   ├── DEVELOPMENT.md          # contributor setup, debugging, testing
│   ├── DEPLOYMENT.md           # running in production (MySQL, packaging)
│   ├── USER_MANUAL.md          # end-user guide
│   ├── SERVICES.md             # service-layer API reference
│   └── screenshots/            # UI screenshots used in the README
├── legacy/                     # the original CLI app, preserved for reference
├── migrations/                 # Alembic environment + versioned migrations
│   ├── env.py
│   └── versions/
├── src/bookshop/               # the application package (src layout)
│   ├── __main__.py             # CLI: run · initdb · seed · info
│   ├── app.py                  # QApplication bootstrap & dependency wiring
│   ├── core/                   # config · security · money · clock · logging · exceptions
│   ├── data/
│   │   ├── base.py             # declarative base, id type, naming convention
│   │   ├── engine.py           # engine + session factory + session_scope
│   │   ├── models/             # user · book · sale (+ sale_item)
│   │   └── repositories/       # user · book · sale (the only place SQL lives)
│   ├── services/               # auth · inventory · sales · analytics · receipt
│   │   ├── dto.py              # frozen data-transfer objects
│   │   ├── container.py        # tiny DI container (Database + services)
│   │   └── seed.py             # demo data
│   └── presentation/           # PySide6 UI (MVVM)
│       ├── context.py          # AppContext handed to views
│       ├── motion.py           # global reduced-motion flag
│       ├── errors.py           # exception → user message
│       ├── theme/              # tokens + theme_manager (QSS) + runtime accent
│       ├── workers/            # QThreadPool worker + TaskRunner
│       ├── widgets/            # design-system components (buttons, table, toast, …)
│       ├── viewmodels/         # one view-model per screen
│       └── views/              # main_window + auth/dashboard/inventory/sell/analytics/settings
├── tests/
│   ├── unit/                   # services, repos, security, money, analytics, schema
│   └── gui/                    # offscreen Qt smoke tests (pytest-qt)
├── pyproject.toml              # packaging, dependencies, tool config
├── docker-compose.yml          # local MySQL 8 + Adminer
├── alembic.ini
├── .env.example  .gitignore  .gitattributes  .pre-commit-config.yaml
├── README.md  LICENSE  CHANGELOG.md
├── CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md
```

## Layering rule

Dependencies point downward only:

```
presentation → services → data → core
```

The presentation layer talks to **services**, never to repositories or the ORM
directly. Services return DTOs (`services/dto.py`), so ORM objects never escape
the data layer.
