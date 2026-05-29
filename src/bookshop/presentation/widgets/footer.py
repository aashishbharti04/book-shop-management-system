"""Persistent application footer with copyright and project/social links."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

# Maintainer / project links (shown in the footer and the About screen).
CONTACT_EMAIL = "aashish@marketdoctorsonline.com"
SOCIAL_LINKS: list[tuple[str, str]] = [
    ("GitHub", "https://github.com/aashishbharti04"),
    ("LinkedIn", "https://in.linkedin.com/in/aashana1012"),
    ("YouTube", "https://www.youtube.com/@CodeWithAsur"),
    ("Instagram", "https://www.instagram.com/asurwave1012?igsh=ZDBlY2NtczJ5cmMw"),
    ("Email", f"mailto:{CONTACT_EMAIL}"),
]
COPYRIGHT = "© 2026 Book Shop Management · All rights reserved · Open source (MIT)"


def links_html(separator: str = "&nbsp;&nbsp;·&nbsp;&nbsp;") -> str:
    return separator.join(f'<a href="{url}">{name}</a>' for name, url in SOCIAL_LINKS)


class FooterBar(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Footer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(8)

        copyright_label = QLabel(COPYRIGHT)
        copyright_label.setProperty("role", "caption")

        links = QLabel(links_html())
        links.setProperty("role", "caption")
        links.setOpenExternalLinks(True)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setAccessibleName("Project and social links")

        layout.addWidget(copyright_label)
        layout.addStretch(1)
        layout.addWidget(links)
