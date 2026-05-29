"""Loading spinner and a blocking loading overlay."""

from __future__ import annotations

from typing import cast

from PySide6.QtCore import QEvent, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..motion import reduced_motion
from ..theme import runtime


class Spinner(QWidget):
    """An indeterminate, theme-coloured spinner."""

    def __init__(self, parent: QWidget | None = None, *, diameter: int = 36, line_width: int = 4) -> None:
        super().__init__(parent)
        self._angle = 0
        self._line_width = line_width
        self.setFixedSize(diameter, diameter)
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0)
        self._anim.setEndValue(360)
        self._anim.setDuration(900)
        self._anim.setLoopCount(-1)
        self._anim.valueChanged.connect(self._on_tick)
        self.setAccessibleName("Loading")

    def _on_tick(self, value: object) -> None:
        self._angle = cast(int, value)
        self.update()

    def start(self) -> None:
        if reduced_motion():
            self._angle = 90
            self.update()
            return
        self._anim.start()

    def stop(self) -> None:
        self._anim.stop()

    def paintEvent(self, event: QEvent) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = self._line_width
        rect = self.rect().adjusted(inset, inset, -inset, -inset)

        track = QPen(QColor(runtime.muted()), self._line_width)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track)
        painter.setOpacity(0.25)
        painter.drawArc(rect, 0, 360 * 16)

        pen = QPen(QColor(runtime.accent()), self._line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setOpacity(1.0)
        painter.drawArc(rect, int(-self._angle * 16), 300 * 16)


class LoadingOverlay(QWidget):
    """A translucent overlay with a centred spinner that blocks its parent."""

    def __init__(self, parent: QWidget, message: str = "Loading…") -> None:
        super().__init__(parent)
        self._target = parent
        self.setObjectName("LoadingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        self.spinner = Spinner(self)
        self.message = QLabel(message)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setProperty("role", "muted")
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message)
        parent.installEventFilter(self)
        self.hide()

    def eventFilter(self, obj: object, event: QEvent) -> bool:  # noqa: N802
        if obj is self._target and event.type() == QEvent.Type.Resize:
            self.setGeometry(self._target.rect())
        return False

    def start(self, message: str | None = None) -> None:
        if message:
            self.message.setText(message)
        self.setGeometry(self._target.rect())
        self.raise_()
        self.show()
        self.spinner.start()

    def stop(self) -> None:
        self.spinner.stop()
        self.hide()
