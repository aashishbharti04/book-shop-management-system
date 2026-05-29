"""The main application window: auth gate, navigation rail, and page host."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ...core.config import get_settings
from ...services.dto import UserDTO
from ..context import AppContext
from ..widgets import FooterBar, ToastManager
from .analytics_view import AnalyticsView
from .auth_view import AuthView
from .dashboard_view import DashboardView
from .inventory_view import InventoryView
from .nav_rail import NavItem, NavRail
from .sell_view import SellView
from .settings_view import SettingsView

COLLAPSE_WIDTH = 900

NAV_ITEMS = [
    NavItem("dashboard", "Dashboard", "📊"),
    NavItem("inventory", "Inventory", "📚"),
    NavItem("sell", "Sell", "🛒"),
    NavItem("analytics", "Analytics", "📈"),
    NavItem("settings", "Settings", "⚙"),
]


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx
        settings = get_settings()
        self.setWindowTitle(settings.app_name)
        self.resize(1180, 760)
        self.setMinimumSize(360, 560)

        central = QWidget()
        central.setObjectName("AppRoot")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.root_stack = QStackedWidget()
        central_layout.addWidget(self.root_stack, 1)
        central_layout.addWidget(FooterBar())  # persistent footer across the app
        self.setCentralWidget(central)

        self.toasts = ToastManager(central)
        ctx.set_notifier(self.toasts.show_message)

        # Pre-auth screen.
        self.auth_view = AuthView(ctx)
        self.auth_view.authenticated.connect(self._on_authenticated)
        self.root_stack.addWidget(self.auth_view)

        # Authenticated application area.
        self.app_container = QWidget()
        app_layout = QHBoxLayout(self.app_container)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        self.nav = NavRail(NAV_ITEMS)
        self.nav.navigated.connect(self.navigate)
        self.nav.themeToggled.connect(self.ctx.theme.toggle_theme)
        self.nav.logoutRequested.connect(self._logout)

        self.page_host = QStackedWidget()
        self.page_host.setObjectName("PageHost")
        page_wrap = QWidget()
        wrap_layout = QVBoxLayout(page_wrap)
        wrap_layout.setContentsMargins(24, 24, 24, 24)
        wrap_layout.addWidget(self.page_host)

        app_layout.addWidget(self.nav)
        app_layout.addWidget(page_wrap, 1)
        self.root_stack.addWidget(self.app_container)

        # Pages are created lazily on first navigation (keeps startup light and
        # defers constructing the matplotlib-backed analytics view until needed).
        self._pages: dict[str, QWidget] = {}
        self._page_factories: dict[str, Callable[[], QWidget]] = self._build_factories()

        self.root_stack.setCurrentWidget(self.auth_view)

    # -- Page construction ---------------------------------------------------
    def _build_factories(self) -> dict[str, Callable[[], QWidget]]:
        ctx = self.ctx
        return {
            "dashboard": lambda: DashboardView(ctx),
            "inventory": lambda: InventoryView(ctx),
            "sell": lambda: SellView(ctx),
            "analytics": lambda: AnalyticsView(ctx),
            "settings": lambda: SettingsView(ctx),
        }

    def _page(self, key: str) -> QWidget | None:
        if key not in self._page_factories:
            return None
        page = self._pages.get(key)
        if page is None:
            page = self._page_factories[key]()
            self._pages[key] = page
            self.page_host.addWidget(page)
        return page

    # -- Navigation / auth ---------------------------------------------------
    def navigate(self, key: str) -> None:
        page = self._page(key)
        if page is None:
            return
        self.page_host.setCurrentWidget(page)
        self.nav.set_active(key)
        refresh = getattr(page, "on_show", None)
        if callable(refresh):
            refresh()

    def _on_authenticated(self, user: UserDTO) -> None:
        self.ctx.current_user = user
        self.nav.set_user(user.username)
        self.root_stack.setCurrentWidget(self.app_container)
        self.navigate("dashboard")
        self.ctx.notify(f"Welcome, {user.username}!", "success")

    def _logout(self) -> None:
        self.ctx.current_user = None
        self.auth_view.reset()
        self.root_stack.setCurrentWidget(self.auth_view)

    # -- Responsive ----------------------------------------------------------
    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.nav.set_collapsed(self.width() < COLLAPSE_WIDTH)
