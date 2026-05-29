"""Transient toast notifications anchored to the top-right of a host widget."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QWidget
from shiboken6 import isValid

from ..motion import reduced_motion
from ..theme import tokens as T

_ICONS = {"success": "✔", "error": "✖", "info": "ℹ", "warning": "⚠"}
_LEVEL_STYLE = {"success": "success", "error": "error", "warning": "info", "info": "info"}
_MARGIN = 16
_GAP = 10


class Toast(QFrame):
    def __init__(self, parent: QWidget, message: str, level: str = "info") -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setProperty("level", _LEVEL_STYLE.get(level, "info"))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(T.SPACE_MD, T.SPACE_SM, T.SPACE_MD, T.SPACE_SM)
        layout.setSpacing(T.SPACE_SM)
        icon = QLabel(_ICONS.get(level, "ℹ"))
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(icon)
        layout.addWidget(message_label, 1)
        self.setMaximumWidth(360)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Accessible announcement.
        self.setAccessibleName(f"{level} notification")
        self.setAccessibleDescription(message)


class ToastManager(QObject):
    """Creates, positions, animates and auto-dismisses toasts over a host."""

    def __init__(self, host: QWidget) -> None:
        super().__init__(host)
        self._host = host
        self._toasts: list[Toast] = []
        self._anims: list[QPropertyAnimation] = []
        host.installEventFilter(self)

    def eventFilter(self, obj: object, event: QEvent) -> bool:  # noqa: N802
        if obj is self._host and event.type() == QEvent.Type.Resize:
            self._reflow()
        return False

    def show_message(self, message: str, level: str = "info", duration: int = 3500) -> None:
        toast = Toast(self._host, message, level)
        toast.adjustSize()
        self._toasts.insert(0, toast)
        toast.show()
        toast.raise_()
        self._reflow(animate_new=toast)
        # Parent the timer to the toast so it is destroyed with it (no stray fire).
        timer = QTimer(toast)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._dismiss(toast))
        timer.start(duration)

    # Convenience helpers --------------------------------------------------
    def success(self, message: str) -> None:
        self.show_message(message, "success")

    def error(self, message: str) -> None:
        self.show_message(message, "error", duration=5000)

    def info(self, message: str) -> None:
        self.show_message(message, "info")

    # Internals ------------------------------------------------------------
    def _target_pos(self, index: int, toast: Toast) -> QPoint:
        x = self._host.width() - toast.width() - _MARGIN
        y = _MARGIN
        for above in self._toasts[:index]:
            y += above.height() + _GAP
        return QPoint(x, y)

    def _reflow(self, animate_new: Toast | None = None) -> None:
        if not isValid(self) or not isValid(self._host):
            return
        self._toasts = [t for t in self._toasts if isValid(t)]
        for index, toast in enumerate(self._toasts):
            target = self._target_pos(index, toast)
            if toast is animate_new and not reduced_motion():
                start = QPoint(self._host.width(), target.y())
                toast.move(start)
                anim = QPropertyAnimation(toast, b"pos", self)
                anim.setDuration(220)
                anim.setStartValue(start)
                anim.setEndValue(target)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.start()
                self._anims.append(anim)
            else:
                toast.move(target)

    def _dismiss(self, toast: Toast) -> None:
        if not isValid(self):
            return
        if toast in self._toasts:
            self._toasts.remove(toast)
        if isValid(toast):
            toast.deleteLater()
        self._reflow()
