"""Current accent colours, published by the theme manager.

Custom-painted widgets (e.g. the spinner) read the accent from here so they
follow the active theme without each needing a reference to the manager.
"""

from __future__ import annotations

_accent = "#6d8cff"
_on_accent = "#ffffff"
_muted = "#9aa3b2"


def set_palette(accent: str, on_accent: str, muted: str) -> None:
    global _accent, _on_accent, _muted
    _accent, _on_accent, _muted = accent, on_accent, muted


def accent() -> str:
    return _accent


def on_accent() -> str:
    return _on_accent


def muted() -> str:
    return _muted
