from __future__ import annotations

import pytest

from bookshop.presentation.workers import TaskRunner


@pytest.mark.gui
def test_task_runner_delivers_result_across_threads(qtbot):
    """Regression: the runner must keep the Worker alive until it finishes.

    Otherwise PySide6 can garbage-collect the Worker/WorkerSignals before the
    pool thread runs, and the result signal is silently lost.
    """

    runner = TaskRunner()
    received: list[object] = []
    finished: list[bool] = []
    runner.run(
        lambda: 21 * 2,
        on_result=received.append,
        on_finished=lambda: finished.append(True),
    )
    qtbot.waitUntil(lambda: bool(finished), timeout=4000)
    assert received == [42]


@pytest.mark.gui
def test_task_runner_routes_errors(qtbot):
    runner = TaskRunner()
    errors: list[BaseException] = []
    finished: list[bool] = []

    def boom() -> None:
        raise ValueError("kaboom")

    runner.run(boom, on_error=errors.append, on_finished=lambda: finished.append(True))
    qtbot.waitUntil(lambda: bool(finished), timeout=4000)
    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)
