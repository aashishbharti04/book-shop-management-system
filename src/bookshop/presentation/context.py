"""Shared application context handed to every view.

Bundles the services, theme manager, async task runner, a notification hook,
and the currently signed-in user, so views don't reach into globals.
"""

from __future__ import annotations

from collections.abc import Callable

from ..services.container import Services
from ..services.dto import UserDTO
from .theme import ThemeManager
from .workers.task_runner import SyncTaskRunner, TaskRunner


class AppContext:
    def __init__(
        self,
        services: Services,
        theme: ThemeManager,
        runner: TaskRunner | SyncTaskRunner,
    ) -> None:
        self.services = services
        self.theme = theme
        self.runner = runner
        self.current_user: UserDTO | None = None
        self._notifier: Callable[[str, str], None] = lambda message, level: None

    def set_notifier(self, notifier: Callable[[str, str], None]) -> None:
        self._notifier = notifier

    def notify(self, message: str, level: str = "info") -> None:
        self._notifier(message, level)
