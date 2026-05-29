from __future__ import annotations

import pytest

from bookshop.presentation.views.main_window import NAV_ITEMS, MainWindow


@pytest.mark.gui
def test_window_registers_all_pages(app_context):
    window = MainWindow(app_context)
    assert window.root_stack.currentWidget() is window.auth_view
    for item in NAV_ITEMS:
        assert item.key in window._page_factories


@pytest.mark.gui
def test_theme_toggle_switches_theme(app_context):
    window = MainWindow(app_context)
    assert window is not None
    before = app_context.theme.theme_name
    app_context.theme.toggle_theme()
    assert app_context.theme.theme_name != before
    assert app_context.theme.theme_name in ("dark", "light")


@pytest.mark.gui
def test_register_authenticates_and_reveals_app(app_context):
    window = MainWindow(app_context)
    auth = window.auth_view
    auth.reg_username.set_text("tester")
    auth.reg_password.set_text("supersecret")
    auth.reg_confirm.set_text("supersecret")
    auth._submit_register()  # SyncTaskRunner runs inline

    assert app_context.current_user is not None
    assert app_context.current_user.username == "tester"
    assert window.root_stack.currentWidget() is window.app_container


@pytest.mark.gui
def test_login_failure_shows_feedback(app_context):
    window = MainWindow(app_context)
    auth = window.auth_view
    auth.login_username.set_text("ghost")
    auth.login_password.set_text("whatever123")
    auth._submit_login()

    assert "Invalid" in auth.feedback.text()
    assert not auth.feedback.isHidden()
    assert window.root_stack.currentWidget() is window.auth_view


@pytest.mark.gui
def test_navigation_switches_pages(app_context):
    window = MainWindow(app_context)
    auth = window.auth_view
    auth.reg_username.set_text("tester")
    auth.reg_password.set_text("supersecret")
    auth.reg_confirm.set_text("supersecret")
    auth._submit_register()

    window.navigate("inventory")
    assert window.page_host.currentWidget() is window._pages["inventory"]
