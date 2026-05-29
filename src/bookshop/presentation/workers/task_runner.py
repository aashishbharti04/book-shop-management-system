"""Dispatch callables to a thread pool (or inline, for tests)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QThreadPool

from .worker import Worker

ResultCb = Callable[[Any], None] | None
ErrorCb = Callable[[BaseException], None] | None
FinishedCb = Callable[[], None] | None


class TaskRunner:
    """Runs callables on a shared ``QThreadPool`` and routes the outcome."""

    def __init__(self, pool: QThreadPool | None = None) -> None:
        self._pool = pool or QThreadPool.globalInstance()
        # Strong references to in-flight workers. Without this, PySide6 may
        # garbage-collect the Python Worker (and its WorkerSignals) before the
        # pool thread finishes, so the result signal would never be delivered.
        self._active: set[Worker] = set()

    def run(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_result: ResultCb = None,
        on_error: ErrorCb = None,
        on_finished: FinishedCb = None,
        **kwargs: Any,
    ) -> Worker:
        worker = Worker(fn, *args, **kwargs)
        self._active.add(worker)
        if on_result is not None:
            worker.signals.result.connect(on_result)
        if on_error is not None:
            worker.signals.error.connect(on_error)
        if on_finished is not None:
            worker.signals.finished.connect(on_finished)
        worker.signals.finished.connect(lambda: self._active.discard(worker))
        self._pool.start(worker)
        return worker


class SyncTaskRunner:
    """Test double: runs the callable inline so signals fire deterministically."""

    def run(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_result: ResultCb = None,
        on_error: ErrorCb = None,
        on_finished: FinishedCb = None,
        **kwargs: Any,
    ) -> None:
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - mirror Worker behaviour
            if on_error is not None:
                on_error(exc)
        else:
            if on_result is not None:
                on_result(result)
        finally:
            if on_finished is not None:
                on_finished()
        return None
