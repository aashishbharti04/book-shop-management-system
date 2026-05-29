"""Skeleton loading placeholders with a gentle pulse animation."""

from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation
from PySide6.QtGui import QHideEvent, QShowEvent
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QVBoxLayout, QWidget

from ..motion import reduced_motion


class SkeletonBar(QFrame):
    def __init__(self, parent: QWidget | None = None, *, height: int = 14, width: int | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Skeleton")
        self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.5)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(1100)
        self._anim.setLoopCount(-1)
        self._anim.setKeyValueAt(0.0, 0.35)
        self._anim.setKeyValueAt(0.5, 0.85)
        self._anim.setKeyValueAt(1.0, 0.35)

    def start(self) -> None:
        if not reduced_motion():
            self._anim.start()

    def stop(self) -> None:
        self._anim.stop()


class SkeletonList(QWidget):
    """A column of skeleton rows; animates while visible."""

    def __init__(self, parent: QWidget | None = None, *, rows: int = 5) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self._bars: list[SkeletonBar] = []
        for _ in range(rows):
            bar = SkeletonBar(self, height=18)
            self._bars.append(bar)
            layout.addWidget(bar)
        layout.addStretch(1)
        self.setAccessibleName("Loading content")

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        for bar in self._bars:
            bar.start()
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        for bar in self._bars:
            bar.stop()
        super().hideEvent(event)
