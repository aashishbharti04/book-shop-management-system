from __future__ import annotations

import pytest
from sqlalchemy import select

from bookshop.core.exceptions import PasswordPolicyError, UsernameTakenError, ValidationError
from bookshop.data.models import User


def test_register_then_login(services):
    user = services.auth.register("alice", "supersecret", "supersecret")
    assert user.id is not None
    assert user.username == "alice"

    logged_in = services.auth.login("alice", "supersecret")
    assert logged_in is not None
    assert logged_in.id == user.id


def test_password_is_hashed_not_stored_plaintext(services, database):
    services.auth.register("bob", "supersecret", "supersecret")
    with database.session_scope() as session:
        stored = session.execute(select(User).where(User.username == "bob")).scalar_one()
        assert stored.password_hash != "supersecret"
        assert stored.password_hash.startswith("$2")  # bcrypt prefix


def test_register_password_mismatch(services):
    with pytest.raises(ValidationError):
        services.auth.register("carol", "supersecret", "different")


def test_register_duplicate_username(services):
    services.auth.register("dave", "supersecret", "supersecret")
    with pytest.raises(UsernameTakenError):
        services.auth.register("dave", "anothersecret", "anothersecret")


def test_register_rejects_weak_password(services):
    with pytest.raises(PasswordPolicyError):
        services.auth.register("erin", "short", "short")


def test_register_requires_username(services):
    with pytest.raises(ValidationError):
        services.auth.register("   ", "supersecret", "supersecret")


def test_login_wrong_password_returns_none(services):
    services.auth.register("frank", "supersecret", "supersecret")
    assert services.auth.login("frank", "wrong") is None


def test_login_unknown_user_returns_none(services):
    assert services.auth.login("nobody", "whatever") is None
