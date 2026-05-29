"""Collapsible left navigation rail."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets import GhostButton

EXPANDED_WIDTH = 224
COLLAPSED_WIDTH = 68


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    icon: str


class NavRail(QWidget):
    navigated = Signal(str)
    themeToggled = Signal()
    logoutRequested = Signal()

    def __init__(self, items: list[NavItem], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._items = items
        self._collapsed = False
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        self.brand = QLabel("📚  BookShop")
        self.brand.setObjectName("SidebarBrand")
        layout.addWidget(self.brand)
        layout.addSpacing(12)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for item in items:
            button = QPushButton(f"{item.icon}   {item.label}")
            button.setProperty("nav", "true")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            button.setAccessibleName(item.label)
            button.setToolTip(item.label)
            button.clicked.connect(lambda _=False, key=item.key: self.navigated.emit(key))
            self._group.addButton(button)
            self._buttons[item.key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        divider = QFrame()
        divider.setObjectName("Separator")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        self.user_label = QLabel("")
        self.user_label.setProperty("role", "caption")
        layout.addWidget(self.user_label)

        self.theme_button = GhostButton("🌗   Theme")
        self.theme_button.setToolTip("Toggle dark / light theme")
        self.theme_button.setAccessibleName("Toggle theme")
        self.theme_button.clicked.connect(self.themeToggled.emit)
        layout.addWidget(self.theme_button)

        self.logout_button = GhostButton("⏏   Sign out")
        self.logout_button.setToolTip("Sign out")
        self.logout_button.setAccessibleName("Sign out")
        self.logout_button.clicked.connect(self.logoutRequested.emit)
        layout.addWidget(self.logout_button)

        self.set_collapsed(False)

    def set_active(self, key: str) -> None:
        button = self._buttons.get(key)
        if button is not None:
            button.setChecked(True)

    def set_user(self, username: str) -> None:
        self._username = username
        self._refresh_texts()

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self.setFixedWidth(COLLAPSED_WIDTH if collapsed else EXPANDED_WIDTH)
        self._refresh_texts()

    def _refresh_texts(self) -> None:
        username = getattr(self, "_username", "")
        if self._collapsed:
            self.brand.setText("📚")
            for item in self._items:
                self._buttons[item.key].setText(item.icon)
            self.theme_button.setText("🌗")
            self.logout_button.setText("⏏")
            self.user_label.setText("")
        else:
            self.brand.setText("📚  BookShop")
            for item in self._items:
                self._buttons[item.key].setText(f"{item.icon}   {item.label}")
            self.theme_button.setText("🌗   Theme")
            self.logout_button.setText("⏏   Sign out")
            self.user_label.setText(f"Signed in as {username}" if username else "")
