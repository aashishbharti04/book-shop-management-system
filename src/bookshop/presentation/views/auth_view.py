"""Pre-authentication screen: sign in or create an account."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ...services.dto import UserDTO
from ..context import AppContext
from ..viewmodels.auth_viewmodel import AuthViewModel
from ..widgets import Card, FormField, GhostButton, PrimaryButton
from .base_view import BaseView


class AuthView(BaseView):
    authenticated = Signal(UserDTO)

    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self.vm = AuthViewModel(ctx, self)
        self._build_ui()
        self._connect()

    # -- UI ------------------------------------------------------------------
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)

        card = Card(object_name="Card")
        card.setFixedWidth(420)
        body = card.body()

        brand = QLabel("📚  Book Shop Management")
        brand.setProperty("role", "h1")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Sign in to manage your shop")
        subtitle.setProperty("role", "muted")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Segmented toggle.
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(0)
        self.tab_login = GhostButton("Sign in")
        self.tab_register = GhostButton("Create account")
        for button in (self.tab_login, self.tab_register):
            button.setCheckable(True)
            button.setProperty("nav", "true")
        self.tab_login.setChecked(True)
        self._tabs = QButtonGroup(self)
        self._tabs.setExclusive(True)
        self._tabs.addButton(self.tab_login, 0)
        self._tabs.addButton(self.tab_register, 1)
        toggle_row.addWidget(self.tab_login)
        toggle_row.addWidget(self.tab_register)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_form())
        self.stack.addWidget(self._build_register_form())

        self.feedback = QLabel("")
        self.feedback.setProperty("role", "error")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback.setWordWrap(True)
        self.feedback.setVisible(False)

        body.addWidget(brand)
        body.addWidget(subtitle)
        body.addSpacing(8)
        body.addLayout(toggle_row)
        body.addWidget(self.stack)
        body.addWidget(self.feedback)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card)
        row.addStretch(1)
        outer.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    def _build_login_form(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        self.login_username = FormField("Username", placeholder="your username")
        self.login_password = FormField("Password", placeholder="your password", password=True)
        self.login_button = PrimaryButton("Sign in")
        layout.addWidget(self.login_username)
        layout.addWidget(self.login_password)
        layout.addWidget(self.login_button)
        layout.addStretch(1)
        self.setTabOrder(self.login_username.input, self.login_password.input)
        self.setTabOrder(self.login_password.input, self.login_button)
        self.login_password.submitted.connect(self._submit_login)
        self.login_username.submitted.connect(self.login_password.focus)
        return page

    def _build_register_form(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        self.reg_username = FormField("Username", placeholder="choose a username")
        self.reg_password = FormField(
            "Password", placeholder="at least 8 characters", password=True
        )
        self.reg_confirm = FormField(
            "Confirm password", placeholder="re-enter password", password=True
        )
        hint = QLabel("Passwords are stored securely (bcrypt-hashed).")
        hint.setProperty("role", "hint")
        self.register_button = PrimaryButton("Create account")
        for widget in (self.reg_username, self.reg_password, self.reg_confirm):
            layout.addWidget(widget)
        layout.addWidget(hint)
        layout.addWidget(self.register_button)
        layout.addStretch(1)
        self.reg_confirm.submitted.connect(self._submit_register)
        return page

    # -- Wiring --------------------------------------------------------------
    def _connect(self) -> None:
        self.tab_login.clicked.connect(lambda: self._switch(0))
        self.tab_register.clicked.connect(lambda: self._switch(1))
        self.login_button.clicked.connect(self._submit_login)
        self.register_button.clicked.connect(self._submit_register)

        self.vm.busyChanged.connect(self._on_busy)
        self.vm.loginSucceeded.connect(self._on_authenticated)
        self.vm.registerSucceeded.connect(self._on_authenticated)
        self.vm.loginFailed.connect(self._on_failed)
        self.vm.registerFailed.connect(self._on_failed)

    def _switch(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self._clear_feedback()

    def _submit_login(self) -> None:
        self._clear_feedback()
        self.vm.login(self.login_username.text(), self.login_password.text())

    def _submit_register(self) -> None:
        self._clear_feedback()
        self.vm.register(
            self.reg_username.text(), self.reg_password.text(), self.reg_confirm.text()
        )

    def _on_busy(self, busy: bool) -> None:
        for button in (self.login_button, self.register_button):
            button.setEnabled(not busy)
        self.login_button.setText("Signing in…" if busy else "Sign in")
        self.register_button.setText("Creating…" if busy else "Create account")

    def _on_authenticated(self, user: UserDTO) -> None:
        self._clear_feedback()
        self.authenticated.emit(user)

    def _on_failed(self, message: str) -> None:
        self.feedback.setText(message)
        self.feedback.setVisible(True)

    def _clear_feedback(self) -> None:
        self.feedback.clear()
        self.feedback.setVisible(False)

    def reset(self) -> None:
        for field in (self.login_password, self.reg_password, self.reg_confirm):
            field.set_text("")
        self._clear_feedback()
