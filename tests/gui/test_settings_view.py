from __future__ import annotations

import pytest

from bookshop.presentation.motion import reduced_motion
from bookshop.presentation.views.settings_view import SettingsView


@pytest.mark.gui
def test_settings_change_theme(app_context):
    view = SettingsView(app_context)
    view.theme_combo.setCurrentIndex(1)  # Light
    assert app_context.theme.theme_name == "light"
    view.theme_combo.setCurrentIndex(0)  # Dark
    assert app_context.theme.theme_name == "dark"


@pytest.mark.gui
def test_settings_change_font_scale(app_context):
    view = SettingsView(app_context)
    view.font_combo.setCurrentIndex(2)  # Large
    assert app_context.theme.font_scale_name == "large"


@pytest.mark.gui
def test_settings_toggle_reduced_motion(app_context):
    view = SettingsView(app_context)
    view.motion_check.setChecked(True)
    assert app_context.theme.reduced_motion is True
    assert reduced_motion() is True
    view.motion_check.setChecked(False)
    assert app_context.theme.reduced_motion is False
