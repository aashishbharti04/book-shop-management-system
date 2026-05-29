"""Runtime theme manager.

Compiles :class:`ThemeTokens` into a Qt style sheet and applies it to the
``QApplication``. Supports switching theme and font scale at runtime, persisting
the choice via :class:`QSettings`, and broadcasting changes via signals.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ...core.config import get_settings
from . import tokens as T
from .tokens import FONT_SCALES, THEMES, ThemeTokens


class ThemeManager(QObject):
    themeChanged = Signal(str)
    fontScaleChanged = Signal(str)

    def __init__(
        self,
        app: QApplication,
        *,
        theme: str | None = None,
        font_scale: str | None = None,
        reduced_motion: bool | None = None,
        persist: bool = True,
    ) -> None:
        super().__init__(app)
        settings = get_settings()
        self._app = app
        self._settings = self._load_qsettings() if persist else None

        stored_theme = self._settings.value("theme", None) if self._settings else None
        stored_scale = self._settings.value("font_scale", None) if self._settings else None
        stored_motion = self._settings.value("reduced_motion", None) if self._settings else None

        self._theme_name = theme or stored_theme or settings.default_theme
        if self._theme_name not in THEMES:
            self._theme_name = "dark"
        self._font_scale = font_scale or stored_scale or settings.font_scale
        if self._font_scale not in FONT_SCALES:
            self._font_scale = "medium"
        if reduced_motion is not None:
            self._reduced_motion = reduced_motion
        elif stored_motion is not None:
            self._reduced_motion = str(stored_motion).lower() in ("1", "true", "yes")
        else:
            self._reduced_motion = settings.reduced_motion

    @staticmethod
    def _load_qsettings():
        from PySide6.QtCore import QSettings

        cfg = get_settings()
        return QSettings(cfg.org_name, cfg.app_name)

    # -- Public API ----------------------------------------------------------

    @property
    def tokens(self) -> ThemeTokens:
        return THEMES[self._theme_name]

    @property
    def theme_name(self) -> str:
        return self._theme_name

    @property
    def scale(self) -> float:
        return FONT_SCALES[self._font_scale]

    @property
    def font_scale_name(self) -> str:
        return self._font_scale

    @property
    def reduced_motion(self) -> bool:
        return self._reduced_motion

    def px(self, value: int) -> int:
        """Scale a pixel value by the current font scale (for code-set sizes)."""

        return max(1, round(value * self.scale))

    def apply(self) -> None:
        """Apply the current theme + font scale to the application."""

        from PySide6.QtGui import QColor, QPalette

        from . import runtime

        self._app.setStyleSheet(build_stylesheet(self.tokens, self.scale))
        font = QFont("Segoe UI", self.px(T.TYPE_BODY))
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self._app.setFont(font)
        # Theme-aware hyperlink colour (QLabel anchors use the palette Link role).
        palette = self._app.palette()
        palette.setColor(QPalette.ColorRole.Link, QColor(self.tokens.primary))
        self._app.setPalette(palette)
        runtime.set_palette(self.tokens.primary, self.tokens.on_primary, self.tokens.text_muted)

    def set_theme(self, name: str) -> None:
        if name not in THEMES or name == self._theme_name:
            return
        self._theme_name = name
        if self._settings:
            self._settings.setValue("theme", name)
        self.apply()
        self.themeChanged.emit(name)

    def toggle_theme(self) -> None:
        self.set_theme("light" if self._theme_name == "dark" else "dark")

    def set_font_scale(self, scale: str) -> None:
        if scale not in FONT_SCALES or scale == self._font_scale:
            return
        self._font_scale = scale
        if self._settings:
            self._settings.setValue("font_scale", scale)
        self.apply()
        self.fontScaleChanged.emit(scale)

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled
        if self._settings:
            self._settings.setValue("reduced_motion", "1" if enabled else "0")


def build_stylesheet(t: ThemeTokens, scale: float) -> str:
    """Compile tokens into a complete Qt style sheet string."""

    def fs(px: int) -> int:
        return max(1, round(px * scale))

    return f"""
/* ---------- Base ---------- */
* {{
    font-family: {T.FONT_FAMILY};
    font-size: {fs(T.TYPE_BODY)}px;
    color: {t.text};
}}
QWidget {{
    background-color: {t.bg};
}}
QWidget:focus {{ outline: none; }}
#AppRoot, #PageHost {{ background-color: {t.bg}; }}

/* ---------- Typography roles ---------- */
QLabel[role="display"] {{ font-size: {fs(T.TYPE_DISPLAY)}px; font-weight: 700; }}
QLabel[role="h1"] {{ font-size: {fs(T.TYPE_H1)}px; font-weight: 700; }}
QLabel[role="h2"] {{ font-size: {fs(T.TYPE_H2)}px; font-weight: 600; }}
QLabel[role="caption"] {{ font-size: {fs(T.TYPE_CAPTION)}px; color: {t.text_muted}; }}
QLabel[role="muted"] {{ color: {t.text_muted}; }}
QLabel[role="metric"] {{ font-size: {fs(T.TYPE_DISPLAY)}px; font-weight: 700; color: {t.primary}; }}
QLabel[role="error"] {{ color: {t.danger}; font-size: {fs(T.TYPE_CAPTION)}px; }}
QLabel[role="hint"] {{ color: {t.text_muted}; font-size: {fs(T.TYPE_CAPTION)}px; }}

/* ---------- Card ---------- */
#Card {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {T.RADIUS_LG}px;
}}
#CardAlt {{
    background-color: {t.surface_alt};
    border: 1px solid {t.border};
    border-radius: {T.RADIUS_MD}px;
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background-color: {t.surface_alt};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: {T.RADIUS_SM}px;
    padding: {fs(8)}px {fs(16)}px;
    font-weight: 600;
}}
QPushButton:hover {{ background-color: {t.border}; }}
QPushButton:focus {{ border: 2px solid {t.focus_ring}; }}
QPushButton:disabled {{ color: {t.text_muted}; background-color: {t.surface}; }}

QPushButton[variant="primary"] {{
    background-color: {t.primary};
    color: {t.on_primary};
    border: 1px solid {t.primary};
}}
QPushButton[variant="primary"]:hover {{ background-color: {t.primary_hover}; border-color: {t.primary_hover}; }}
QPushButton[variant="primary"]:pressed {{ background-color: {t.primary_pressed}; }}
QPushButton[variant="primary"]:disabled {{ background-color: {t.surface_alt}; color: {t.text_muted}; border-color: {t.border}; }}

QPushButton[variant="ghost"] {{ background-color: transparent; border: 1px solid transparent; }}
QPushButton[variant="ghost"]:hover {{ background-color: {t.surface_alt}; }}

QPushButton[variant="danger"] {{ background-color: {t.danger}; color: {t.text_inverse}; border-color: {t.danger}; }}
QPushButton[variant="danger"]:hover {{ background-color: {t.danger_hover}; border-color: {t.danger_hover}; }}

/* ---------- Sidebar / navigation ---------- */
#Sidebar {{ background-color: {t.surface}; border-right: 1px solid {t.border}; }}
#SidebarBrand {{ font-size: {fs(T.TYPE_H2)}px; font-weight: 700; color: {t.text}; }}
QPushButton[nav="true"] {{
    background-color: transparent;
    border: none;
    border-radius: {T.RADIUS_SM}px;
    padding: {fs(10)}px {fs(14)}px;
    text-align: left;
    color: {t.text_muted};
    font-weight: 600;
}}
QPushButton[nav="true"]:hover {{ background-color: {t.surface_alt}; color: {t.text}; }}
QPushButton[nav="true"]:checked {{ background-color: {t.selection}; color: {t.text}; }}
QPushButton[nav="true"]:focus {{ border: 2px solid {t.focus_ring}; }}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit, QDateEdit {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {T.RADIUS_SM}px;
    padding: {fs(7)}px {fs(10)}px;
    selection-background-color: {t.primary};
    selection-color: {t.on_primary};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QDateEdit:focus {{
    border: 2px solid {t.focus_ring};
}}
QLineEdit[invalid="true"], QComboBox[invalid="true"], QSpinBox[invalid="true"] {{
    border: 1px solid {t.danger};
}}
QLineEdit::placeholder {{ color: {t.text_muted}; }}
QComboBox::drop-down {{ border: none; width: {fs(20)}px; }}
QComboBox QAbstractItemView {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    selection-background-color: {t.selection};
    selection-color: {t.text};
    outline: none;
}}

/* ---------- Table ---------- */
QTableView {{
    background-color: {t.surface};
    alternate-background-color: {t.surface_alt};
    border: 1px solid {t.border};
    border-radius: {T.RADIUS_MD}px;
    gridline-color: {t.border};
    selection-background-color: {t.selection};
    selection-color: {t.text};
}}
QTableView::item {{ padding: {fs(6)}px {fs(8)}px; }}
QHeaderView::section {{
    background-color: {t.surface_alt};
    color: {t.text_muted};
    padding: {fs(8)}px;
    border: none;
    border-bottom: 1px solid {t.border};
    font-weight: 600;
}}
QTableView QTableCornerButton::section {{ background-color: {t.surface_alt}; border: none; }}

/* ---------- Badges ---------- */
QLabel[badge="success"] {{ background-color: {t.success_bg}; color: {t.success}; border-radius: {T.RADIUS_SM}px; padding: {fs(2)}px {fs(8)}px; font-weight: 600; font-size: {fs(T.TYPE_CAPTION)}px; }}
QLabel[badge="warning"] {{ background-color: {t.warning_bg}; color: {t.warning}; border-radius: {T.RADIUS_SM}px; padding: {fs(2)}px {fs(8)}px; font-weight: 600; font-size: {fs(T.TYPE_CAPTION)}px; }}
QLabel[badge="danger"] {{ background-color: {t.danger_bg}; color: {t.danger}; border-radius: {T.RADIUS_SM}px; padding: {fs(2)}px {fs(8)}px; font-weight: 600; font-size: {fs(T.TYPE_CAPTION)}px; }}

/* ---------- Toast ---------- */
#Toast {{ border-radius: {T.RADIUS_MD}px; padding: {fs(10)}px {fs(14)}px; color: {t.text}; background-color: {t.surface_alt}; border: 1px solid {t.border}; }}
#Toast[level="success"] {{ border-left: 4px solid {t.success}; }}
#Toast[level="error"] {{ border-left: 4px solid {t.danger}; }}
#Toast[level="info"] {{ border-left: 4px solid {t.primary}; }}

/* ---------- Skeleton / overlay ---------- */
#Skeleton {{ background-color: {t.surface_alt}; border-radius: {T.RADIUS_SM}px; }}
#LoadingOverlay {{ background-color: {t.overlay}; }}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {{ background: transparent; width: {fs(10)}px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {t.border}; border-radius: {fs(5)}px; min-height: {fs(24)}px; }}
QScrollBar::handle:vertical:hover {{ background: {t.text_muted}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: {fs(10)}px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {t.border}; border-radius: {fs(5)}px; min-width: {fs(24)}px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ---------- Footer ---------- */
#Footer {{ background-color: {t.surface}; border-top: 1px solid {t.border}; }}
#Footer QLabel {{ color: {t.text_muted}; }}

/* ---------- Misc ---------- */
QToolTip {{ background-color: {t.surface_alt}; color: {t.text}; border: 1px solid {t.border}; padding: {fs(4)}px {fs(8)}px; border-radius: {T.RADIUS_SM}px; }}
#Separator {{ background-color: {t.border}; }}
QCheckBox {{ spacing: {fs(8)}px; }}
QCheckBox::indicator {{ width: {fs(16)}px; height: {fs(16)}px; border: 1px solid {t.border}; border-radius: {T.RADIUS_SM // 2}px; background: {t.surface}; }}
QCheckBox::indicator:checked {{ background: {t.primary}; border-color: {t.primary}; }}
"""
