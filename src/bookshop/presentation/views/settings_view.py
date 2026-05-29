"""Settings: appearance and accessibility preferences."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ... import __version__
from ...core.config import get_settings
from ..context import AppContext
from ..motion import set_reduced_motion
from ..widgets import Card
from ..widgets.footer import links_html
from .base_view import BaseView


def _row(label_text: str, control: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    label = QLabel(label_text)
    label.setBuddy(control)
    row.addWidget(label)
    row.addStretch(1)
    row.addWidget(control)
    return row


class SettingsView(BaseView):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self._build_ui()
        self._connect()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("Settings")
        title.setProperty("role", "h1")
        root.addWidget(title)

        appearance = Card()
        heading = QLabel("Appearance & accessibility")
        heading.setProperty("role", "h2")
        appearance.body().addWidget(heading)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.setCurrentIndex(0 if self.ctx.theme.theme_name == "dark" else 1)
        self.theme_combo.setAccessibleName("Theme")

        self.font_combo = QComboBox()
        for label, value in (("Small", "small"), ("Medium", "medium"), ("Large", "large")):
            self.font_combo.addItem(label, value)
        self.font_combo.setCurrentIndex(
            {"small": 0, "medium": 1, "large": 2}.get(self.ctx.theme.font_scale_name, 1)
        )
        self.font_combo.setAccessibleName("Text size")

        self.motion_check = QCheckBox("Reduce motion (disable animations)")
        self.motion_check.setChecked(self.ctx.theme.reduced_motion)
        self.motion_check.setAccessibleName("Reduce motion")

        appearance.body().addLayout(_row("Theme", self.theme_combo))
        appearance.body().addLayout(_row("Text size", self.font_combo))
        appearance.body().addWidget(self.motion_check)
        root.addWidget(appearance)

        about = Card()
        about_heading = QLabel("About")
        about_heading.setProperty("role", "h2")
        about.body().addWidget(about_heading)
        info = QLabel(
            f"{get_settings().app_name}  ·  version {__version__}\n"
            "Open-source under the MIT License."
        )
        info.setProperty("role", "muted")
        info.setWordWrap(True)
        about.body().addWidget(info)

        links = QLabel(f"Connect: {links_html()}")
        links.setProperty("role", "caption")
        links.setOpenExternalLinks(True)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setAccessibleName("Project and social links")
        about.body().addWidget(links)
        root.addWidget(about)
        root.addStretch(1)

    def _connect(self) -> None:
        self.theme_combo.currentIndexChanged.connect(self._on_theme)
        self.font_combo.currentIndexChanged.connect(self._on_font)
        self.motion_check.toggled.connect(self._on_motion)

    def _on_theme(self) -> None:
        self.ctx.theme.set_theme(self.theme_combo.currentData())

    def _on_font(self) -> None:
        self.ctx.theme.set_font_scale(self.font_combo.currentData())

    def _on_motion(self, checked: bool) -> None:
        self.ctx.theme.set_reduced_motion(checked)
        set_reduced_motion(checked)
        self.ctx.notify("Motion settings updated.", "info")
