"""A generic background worker.

``QRunnable`` is not a ``QObject``, so its signals must live on a separate
:class:`WorkerSignals` object. Cross-thread signal connections are delivered as
queued connections, marshalling results safely back to the GUI thread.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ...core.logging import get_logger

_log = get_logger("bookshop.worker")


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(object)  # carries the raised Exception instance
    finished = Signal()


class Worker(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(*self._args, **self._kwargs)
        except Exception as exc:  # noqa: BLE001 - report all failures to the UI
            _log.exception("Background task failed: %s", exc)
            self.signals.error.emit(exc)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
