"""A labelled input with inline validation messaging and accessibility wiring."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from .utils import repolish


class FormField(QWidget):
    """Composes a label, an input widget, and an inline error message."""

    submitted = Signal()

    def __init__(
        self,
        label: str,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        password: bool = False,
        widget: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.label = QLabel(label)
        self.label.setProperty("role", "caption")

        self.input: QWidget = widget or QLineEdit()
        if isinstance(self.input, QLineEdit):
            self.input.setPlaceholderText(placeholder)
            if password:
                self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self.input.textChanged.connect(lambda *_: self.clear_error())
            self.input.returnPressed.connect(self.submitted.emit)

        self.error = QLabel("")
        self.error.setProperty("role", "error")
        self.error.setWordWrap(True)
        self.error.setVisible(False)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.error)

        # Accessibility: associate the label with the field for screen readers.
        self.input.setAccessibleName(label)
        if hasattr(self.label, "setBuddy"):
            self.label.setBuddy(self.input)

    def text(self) -> str:
        getter = getattr(self.input, "text", None)
        return getter() if callable(getter) else ""

    def set_text(self, value: str) -> None:
        setter = getattr(self.input, "setText", None)
        if callable(setter):
            setter(value)

    def set_error(self, message: str) -> None:
        self.error.setText(message)
        self.error.setVisible(bool(message))
        self.input.setProperty("invalid", bool(message))
        repolish(self.input)
        if message:
            self.input.setAccessibleDescription(message)

    def clear_error(self) -> None:
        if self.error.isVisible() or self.input.property("invalid"):
            self.set_error("")

    def focus(self) -> None:
        self.input.setFocus()
