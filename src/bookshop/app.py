"""Application bootstrap: build the QApplication, theme, services and window.

``QT_API`` is pinned to PySide6 *before* anything (e.g. matplotlib) can bind to
a different Qt binding.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_API", "pyside6")

from .core.config import get_settings
from .core.logging import get_logger


def create_application(argv: list[str] | None = None):
    from typing import cast

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = cast(QApplication, QApplication.instance() or QApplication(list(argv or [])))
    settings = get_settings()
    app.setApplicationName(settings.app_name)
    app.setApplicationDisplayName(settings.app_name)
    app.setOrganizationName(settings.org_name)
    return app


def run(argv: list[str] | None = None) -> int:
    log = get_logger("bookshop.app")
    app = create_application(argv)

    from .presentation.context import AppContext
    from .presentation.motion import set_reduced_motion
    from .presentation.theme import ThemeManager
    from .presentation.views.main_window import MainWindow
    from .presentation.workers import TaskRunner
    from .services.container import Container

    theme = ThemeManager(app)
    set_reduced_motion(theme.reduced_motion)
    theme.apply()
    theme.fontScaleChanged.connect(lambda *_: set_reduced_motion(theme.reduced_motion))

    container = Container()
    container.database.create_all()  # ensure schema exists on first launch
    ctx = AppContext(container.services, theme, TaskRunner())

    window = MainWindow(ctx)
    window.show()
    log.info("Application started (theme=%s, scale=%s).", theme.theme_name, theme.scale)
    return app.exec()
