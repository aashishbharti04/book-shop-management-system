"""Small widget helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget


def repolish(widget: QWidget) -> None:
    """Re-evaluate a widget's style after a dynamic property change."""

    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_property(widget: QWidget, name: str, value: object) -> None:
    """Set a Qt dynamic property and immediately restyle the widget."""

    widget.setProperty(name, value)
    repolish(widget)
