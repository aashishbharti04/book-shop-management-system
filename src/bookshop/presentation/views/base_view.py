"""Base class for views, with an async helper and error-to-message mapping."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import QWidget

from ..context import AppContext
from ..errors import humanize_error

__all__ = ["BaseView", "humanize_error"]


class BaseView(QWidget):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ctx = ctx

    def run_async(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_result: Callable[[Any], None] | None = None,
        on_error: Callable[[BaseException], None] | None = None,
        on_finished: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        """Run *fn* off the UI thread, routing errors to a toast by default."""

        def default_error(exc: BaseException) -> None:
            self.ctx.notify(humanize_error(exc), "error")

        self.ctx.runner.run(
            fn,
            *args,
            on_result=on_result,
            on_error=on_error or default_error,
            on_finished=on_finished,
            **kwargs,
        )
