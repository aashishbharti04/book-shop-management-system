"""Global reduced-motion flag for accessibility.

Animated widgets consult :func:`reduced_motion` and skip or shorten animations
when it is enabled. The application wires this to the theme manager / settings.
"""

from __future__ import annotations

_reduced_motion = False


def set_reduced_motion(enabled: bool) -> None:
    global _reduced_motion
    _reduced_motion = bool(enabled)


def reduced_motion() -> bool:
    return _reduced_motion
