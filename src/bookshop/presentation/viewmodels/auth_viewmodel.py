"""View-model for authentication screens."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ...services.dto import UserDTO
from ..context import AppContext
from ..errors import humanize_error


class AuthViewModel(QObject):
    busyChanged = Signal(bool)
    loginSucceeded = Signal(UserDTO)
    loginFailed = Signal(str)
    registerSucceeded = Signal(UserDTO)
    registerFailed = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def login(self, username: str, password: str) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            self._ctx.services.auth.login,
            username,
            password,
            on_result=self._on_login_result,
            on_error=self._on_login_error,
            on_finished=lambda: self.busyChanged.emit(False),
        )

    def register(self, username: str, password: str, confirm: str) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            self._ctx.services.auth.register,
            username,
            password,
            confirm,
            on_result=self.registerSucceeded.emit,
            on_error=self._on_register_error,
            on_finished=lambda: self.busyChanged.emit(False),
        )

    def _on_login_result(self, user: object) -> None:
        if user is None:
            self.loginFailed.emit("Invalid username or password.")
        else:
            self.loginSucceeded.emit(user)

    def _on_login_error(self, exc: BaseException) -> None:
        self.loginFailed.emit(humanize_error(exc))

    def _on_register_error(self, exc: BaseException) -> None:
        self.registerFailed.emit(humanize_error(exc))
