"""Design tokens — the single source of truth for colour, type and spacing.

Two themes (:data:`DARK` and :data:`LIGHT`) are defined as :class:`ThemeTokens`
instances. The :class:`~bookshop.presentation.theme.theme_manager.ThemeManager`
compiles these into a Qt style sheet, so changing a colour in one place restyles
the whole application.
"""

from __future__ import annotations

from dataclasses import dataclass

# Spacing scale (px) — a consistent rhythm used throughout the UI.
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
SPACE_XXL = 32

# Corner radii.
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 16

# Base type scale (px at scale = 1.0).
TYPE_DISPLAY = 28
TYPE_H1 = 22
TYPE_H2 = 18
TYPE_BODY = 13
TYPE_CAPTION = 11

FONT_FAMILY = "Segoe UI, Inter, system-ui, Arial, sans-serif"

# Multipliers for the accessibility font-scale setting.
FONT_SCALES: dict[str, float] = {"small": 0.9, "medium": 1.0, "large": 1.18}


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    name: str
    is_dark: bool

    # Surfaces / structure
    bg: str
    surface: str
    surface_alt: str
    border: str
    overlay: str  # rgba string for modal/loading overlays

    # Text
    text: str
    text_muted: str
    text_inverse: str

    # Brand / actions
    primary: str
    primary_hover: str
    primary_pressed: str
    on_primary: str
    focus_ring: str

    # Semantic
    success: str
    success_bg: str
    warning: str
    warning_bg: str
    danger: str
    danger_bg: str
    danger_hover: str

    # Misc
    shadow: str  # rgba for drop shadows
    selection: str


DARK = ThemeTokens(
    name="dark",
    is_dark=True,
    bg="#0f1117",
    surface="#181b24",
    surface_alt="#1f2330",
    border="#2a2f3d",
    overlay="rgba(8, 10, 16, 160)",
    text="#e7e9ee",
    text_muted="#9aa3b2",
    text_inverse="#0f1117",
    primary="#6d8cff",
    primary_hover="#7e9aff",
    primary_pressed="#5a78e6",
    on_primary="#ffffff",
    focus_ring="#8aa0ff",
    success="#34d399",
    success_bg="#10291f",
    warning="#fbbf24",
    warning_bg="#2a2310",
    danger="#f87171",
    danger_bg="#2a1414",
    danger_hover="#fb8a8a",
    shadow="rgba(0, 0, 0, 110)",
    selection="#2c3550",
)

LIGHT = ThemeTokens(
    name="light",
    is_dark=False,
    bg="#f4f6f9",
    surface="#ffffff",
    surface_alt="#eef1f6",
    border="#d8dee8",
    overlay="rgba(20, 24, 33, 90)",
    text="#1a1f2b",
    text_muted="#5b6573",
    text_inverse="#ffffff",
    primary="#4f6ef2",
    primary_hover="#4060e6",
    primary_pressed="#3552cf",
    on_primary="#ffffff",
    focus_ring="#4f6ef2",
    success="#059669",
    success_bg="#e6f6ef",
    warning="#b45309",
    warning_bg="#fdf0dc",
    danger="#dc2626",
    danger_bg="#fbe9e9",
    danger_hover="#c41f1f",
    shadow="rgba(20, 30, 60, 40)",
    selection="#dbe4ff",
)

THEMES: dict[str, ThemeTokens] = {DARK.name: DARK, LIGHT.name: LIGHT}
